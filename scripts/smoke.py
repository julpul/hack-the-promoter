#!/usr/bin/env python3
"""Smoke test API: sprawdza, czy wszystkie endpointy odpowiadaja.

    python scripts/smoke.py            # bez /wgraj (bezpieczne, mozna czesto)
    python scripts/smoke.py --wgraj    # dodatkowo probne zgloszenie 1 sekwencji
                                       # UWAGA: zjada okno 5 minut!

Kod wyjscia 0 = wszystko OK, 1 = cos nie dziala.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hyppe import ApiError, Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

ZIELONY, CZERWONY, ZOLTY, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


class Smoke:
    def __init__(self):
        self.bledy = 0
        self.pominiete = 0

    def krok(self, nazwa, fn):
        t0 = time.monotonic()
        try:
            wynik = fn()
        except Exception as e:  # noqa: BLE001 -- smoke ma zlapac wszystko
            self.bledy += 1
            print(f"{CZERWONY}FAIL{RESET} {nazwa:<28} {type(e).__name__}: {e}")
            return None
        dt = time.monotonic() - t0
        opis = wynik[1] if isinstance(wynik, tuple) else ""
        print(f"{ZIELONY} OK {RESET} {nazwa:<28} {dt:6.2f}s  {opis}")
        return wynik[0] if isinstance(wynik, tuple) else wynik

    def pomin(self, nazwa, powod):
        self.pominiete += 1
        print(f"{ZOLTY}SKIP{RESET} {nazwa:<28} {powod}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wgraj", action="store_true",
                    help="wykonaj takze probne POST /wgraj (blokuje na 5 min)")
    ap.add_argument("--api-key")
    ap.add_argument("--url")
    a = ap.parse_args()

    sm = Smoke()
    try:
        c = Client.from_env(api_key=a.api_key, url=a.url)
    except RuntimeError as e:
        print(f"{CZERWONY}FAIL{RESET} konfiguracja: {e}")
        return 1
    print(f"API: {c.cfg.url}  klucz: ...{c.cfg.api_key[-6:]}\n")

    def _me():
        j = c.me()
        return j, f"druzyna={j.get('druzyna')} wgranie_za={j.get('zgloszenie_mozliwe_za_s')}s"

    ja = sm.krok("GET /me", _me)

    def _dziki():
        d = c.dziki()
        assert len(d["sekwencja"]) == 800, "dziki nie ma 800 pz"
        assert not F.problemy(d["sekwencja"]), F.problemy(d["sekwencja"])
        return d, f"{d.get('gen')} GC={S.gc(d['sekwencja']):.1%} sha={d.get('sha256_12')}"

    d = sm.krok("GET /dziki", _dziki)
    if not d:
        print("\nbez sekwencji bazowej nie ma sensu isc dalej")
        return 1
    dziki = d["sekwencja"]

    def _mapa():
        m = c.mapa(dziki, od=0, ile=800)
        assert len(m["pozycje"]) > 0
        rek = sum(1 for w in m["pozycje"] if w["zmien_na"] != ".")
        return m, f"gatunek={m.get('gatunek')} rekomendacji={rek}"

    m = sm.krok("POST /nawigator/mapa", _mapa)

    def _edycje():
        e = c.edycje(dziki, poziom=2, ile_kodow=8, opcji=4, ziarno=1)
        assert e["opcje"], "brak opcji"
        for o in e["opcje"]:
            assert len(o["sekwencja"]) == 800
        return e, f"warstwa={e.get('warstwa')} opcji={len(e['opcje'])}"

    e = sm.krok("POST /nawigator/edycje", _edycje)

    kandydat = c.zastosuj_rekomendacje(dziki, m) if m else None
    if kandydat is None or kandydat == dziki:
        kandydat = e["opcje"][0]["sekwencja"] if e else S.mutuj(dziki, ile=10, ziarno=1)

    def _sedzia():
        w = c.sedzia(dziki, kandydat, "dziki", "kandydat")
        assert w.get("silniejsza_idx") in (0, 1), w
        return w, f"silniejsza={w.get('silniejsza')} (idx {w.get('silniejsza_idx')})"

    sm.krok("POST /sedzia", _sedzia)

    def _ranking():
        t = c.ranking()
        return t, f"druzyn={t.get('n_druzyn')} nasza_pozycja={t.get('twoja_pozycja')}"

    sm.krok("GET /ranking", _ranking)

    czekaj = (ja or {}).get("zgloszenie_mozliwe_za_s") or 0
    if not a.wgraj:
        sm.pomin("POST /wgraj", "domyslnie pominiete, dodaj --wgraj")
    elif czekaj:
        sm.pomin("POST /wgraj", f"okno zajete jeszcze {czekaj}s")
    else:
        def _wgraj():
            tekst = F.na_tekst([("smoke_dziki", dziki)])
            r = c.wgraj(tekst)
            return r, f"ocenionych={r.get('ocenionych')} punkty={r.get('punkty_razem')}"

        sm.krok("POST /wgraj", _wgraj)

    print()
    if sm.bledy:
        print(f"{CZERWONY}{sm.bledy} endpoint(ow) nie dziala{RESET}")
        return 1
    print(f"{ZIELONY}wszystko OK{RESET}" + (f", pominieto {sm.pominiete}" if sm.pominiete else ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ApiError as err:
        print(f"{CZERWONY}FAIL{RESET} {err}")
        sys.exit(1)
