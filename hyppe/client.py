"""Klient HTTP API hackathonu (tylko biblioteka standardowa).

Uzycie z kodu:

    from hyppe import Client
    c = Client.from_env()
    dziki = c.dziki()["sekwencja"]
    print(c.sedzia(dziki, kandydat)["silniejsza_idx"])
"""

from __future__ import annotations

import http.client
import json
import threading
import time
import urllib.error
import urllib.request
from typing import Any

from .config import Config

# 5xx bramy/originu -- z definicji przejsciowe. 530 = Cloudflare 1033 (origin
# chwilowo nieosiagalny), potrafi wrocic samo w kilka sekund.
KODY_PONAWIALNE = frozenset({500, 502, 503, 504, 520, 521, 522, 523, 524, 530})


def rownolegle(fn, elementy, watkow: int = 16, na_blad=None):
    """Mapuje `fn` po `elementach` w puli watkow, zachowujac kolejnosc wejscia.

    Limitery w `Client` sa pod lockiem, wiec wolanie z wielu watkow jest
    bezpieczne. Wyjatek w `fn` daje `na_blad` na tej pozycji -- pojedyncze
    zerwane polaczenie nie moze wywrocic calego przebiegu.
    """
    from concurrent.futures import ThreadPoolExecutor

    def bezpiecznie(x):
        try:
            return fn(x)
        except Exception:                                    # noqa: BLE001
            return na_blad

    elementy = list(elementy)
    if not elementy:
        return []
    with ThreadPoolExecutor(max_workers=min(watkow, len(elementy))) as pula:
        return list(pula.map(bezpiecznie, elementy))


class ApiError(RuntimeError):
    def __init__(self, kod: int, tresc: Any, sciezka: str):
        self.kod = kod
        self.tresc = tresc
        self.sciezka = sciezka
        super().__init__(f"HTTP {kod} na {sciezka}: {tresc}")


class RateLimiter:
    """Prosty limiter: nie wiecej niz `na_minute` wywolan w oknie 60 s."""

    def __init__(self, na_minute: int):
        self.na_minute = na_minute
        self._czasy: list[float] = []
        self._lock = threading.Lock()

    def czekaj(self) -> None:
        if self.na_minute <= 0:
            return
        while True:
            with self._lock:
                teraz = time.monotonic()
                self._czasy = [t for t in self._czasy if teraz - t < 60.0]
                if len(self._czasy) < self.na_minute:
                    self._czasy.append(teraz)
                    return
                spac = 60.0 - (teraz - self._czasy[0]) + 0.01
            time.sleep(spac)


# Limity odczytane z /me (2026-08-29 18:39): sedzia/mapa/edycje 3000/min,
# inne 600/min. Trzymamy 5% zapasu, zeby nie ocierac sie o 429.
# UWAGA: wczesniej stalo tu 570/570/570 -- piec razy ponizej faktycznego
# limitu. Kazdy eksperyment z pierwszej polowy dnia byl przez to dlawiony.
LIMITY = {
    "/sedzia": 2850,
    "/nawigator/mapa": 2850,
    "/nawigator/edycje": 2850,
    "_post": 570,
}


class Client:
    def __init__(self, cfg: Config, przestrzegaj_limitow: bool = True):
        self.cfg = cfg
        self._limitery = (
            {k: RateLimiter(v) for k, v in LIMITY.items()}
            if przestrzegaj_limitow
            else {}
        )

    @classmethod
    def from_env(cls, api_key: str | None = None, url: str | None = None, **kw) -> "Client":
        return cls(Config.from_env(api_key=api_key, url=url), **kw)

    # ---------- warstwa transportu ----------

    def wolaj(self, sciezka: str, dane: dict | None = None) -> tuple[int, Any]:
        """Zwraca (kod_http, odpowiedz). `dane` != None -> POST z JSON-em.

        Ponawia 503 oraz 429 (poza /wgraj, gdzie 429 znaczy 'czekaj 5 min').
        """
        limiter = self._limitery.get(sciezka)
        if limiter is None and dane is not None:
            limiter = self._limitery.get("_post")
        if limiter is not None:
            limiter.czekaj()

        for nr in range(self.cfg.retries):
            z = urllib.request.Request(self.cfg.url.rstrip("/") + sciezka)
            z.add_header("X-API-Key", self.cfg.api_key)
            z.add_header("User-Agent", self.cfg.user_agent)
            if dane is not None:
                z.add_header("Content-Type", "application/json")
                z.data = json.dumps(dane).encode()
            try:
                with urllib.request.urlopen(z, timeout=self.cfg.timeout) as o:
                    return o.status, json.loads(o.read().decode())
            except urllib.error.HTTPError as e:
                tresc = e.read().decode("utf-8", "replace")
                try:
                    tresc = json.loads(tresc)
                except Exception:
                    pass
                ponawialne = e.code in KODY_PONAWIALNE or (
                    e.code == 429 and sciezka != "/wgraj")
                if not ponawialne or nr == self.cfg.retries - 1:
                    return e.code, tresc
                czekaj = float(e.headers.get("Retry-After") or 0) or 0.4 * 2**nr
                time.sleep(min(czekaj, 8.0))
            except (OSError, http.client.HTTPException) as e:
                # OSError lapie tez urllib.error.URLError i ConnectionResetError.
                # RemoteDisconnected NIE jest podklasa URLError, a przy kilkuset
                # wywolaniach na eksperyment zrywa sie regularnie -- bez tego
                # przebieg pada w polowie i traci wszystkie zebrane pomiary.
                if nr == self.cfg.retries - 1:
                    return 0, f"siec: {type(e).__name__}: {e}"
                time.sleep(0.4 * 2**nr)
        return 0, "wyczerpano proby"

    def _ok(self, sciezka: str, dane: dict | None = None) -> Any:
        kod, odp = self.wolaj(sciezka, dane)
        if kod != 200:
            raise ApiError(kod, odp, sciezka)
        return odp

    # ---------- endpointy ----------

    def me(self) -> dict:
        return self._ok("/me")

    def dziki(self) -> dict:
        """Promotor wyjsciowy pks1 (800 pz)."""
        return self._ok("/dziki")

    def dziki_seq(self) -> str:
        return self.dziki()["sekwencja"]

    def sedzia(self, a: str, b: str, nazwa_a: str = "a", nazwa_b: str = "b") -> dict:
        """Porownanie pary. Zwraca m.in. `silniejsza` i `silniejsza_idx` (0/1)."""
        return self._ok(
            "/sedzia", {"a": a, "b": b, "nazwa_a": nazwa_a, "nazwa_b": nazwa_b}
        )

    def lepsza(self, a: str, b: str) -> bool:
        """True, jesli Sedzia wskazal `b` jako silniejsza."""
        return self.sedzia(a, b).get("silniejsza_idx") == 1

    def mapa(self, sekwencja: str, od: int = 0, ile: int = 800) -> dict:
        return self._ok(
            "/nawigator/mapa", {"sekwencja": sekwencja, "od": od, "ile": ile}
        )

    def edycje(
        self,
        sekwencja: str,
        poziom: int = 2,
        ile_kodow: int = 8,
        opcji: int = 8,
        ziarno: int | None = None,
    ) -> dict:
        dane: dict = {
            "sekwencja": sekwencja,
            "poziom": poziom,
            "ile_kodow": ile_kodow,
            "opcji": opcji,
        }
        if ziarno is not None:
            dane["ziarno"] = ziarno
        return self._ok("/nawigator/edycje", dane)

    def wgraj(self, fasta: str) -> dict:
        """Zgloszenie pliku FASTA (raz na 5 min). 429 -> ApiError."""
        return self._ok("/wgraj", {"fasta": fasta})

    def ranking(self) -> dict:
        return self._ok("/ranking")

    # ---------- warstwa wygody ----------

    def zastosuj_rekomendacje(self, sekwencja: str, mapa: dict | None = None) -> str:
        """Nanosi wszystkie `zmien_na` z mapy Nawigatora na sekwencje."""
        m = mapa if mapa is not None else self.mapa(sekwencja)
        out = list(sekwencja)
        for w in m["pozycje"]:
            if w["zmien_na"] != ".":
                out[w["poz"] - 1] = w["zmien_na"]
        return "".join(out)

    def turniej(self, baza: str, kandydaci: dict[str, str]) -> list[tuple[str, str]]:
        """Zwraca [(etykieta, sekwencja)] kandydatow, ktorzy przebili `baza`."""
        wygrane = []
        for etyk, seq in kandydaci.items():
            if self.lepsza(baza, seq):
                wygrane.append((etyk, seq))
        return wygrane

    def ranking_swiss(self, kandydaci: dict[str, str], rund: int = 5) -> list[tuple[str, int, str]]:
        """Turniej systemem szwajcarskim -- tanszy niz kazdy-z-kazdym.

        Zwraca [(etykieta, punkty, sekwencja)] posortowane malejaco.
        """
        pozycje = list(kandydaci.items())
        punkty = {e: 0 for e, _ in pozycje}
        for _ in range(rund):
            uporzadkowane = sorted(pozycje, key=lambda p: -punkty[p[0]])
            for i in range(0, len(uporzadkowane) - 1, 2):
                (ea, sa), (eb, sb) = uporzadkowane[i], uporzadkowane[i + 1]
                if self.lepsza(sa, sb):
                    punkty[eb] += 1
                else:
                    punkty[ea] += 1
        return sorted(
            ((e, punkty[e], s) for e, s in pozycje), key=lambda t: -t[1]
        )
