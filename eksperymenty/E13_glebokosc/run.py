#!/usr/bin/env python3
"""E13 -- pchniecie osi, ktora JAKO JEDYNA dala duzy zysk.

Przejscie przez dekoder to jedyna interwencja z duzym efektem:
dziki 5,0 pkt -> ziarna 14,0 pkt (piec pozycji rankingu). Wszystkie dodatki
nakladane pozniej (CCAAT, gatunek, poli-AT, tandem, CreA, swiatlo) mieszcza
sie w pasmie 12-14, czyli w szumie wokol plateau.

Dwa nieprzetestowane sposoby pchniecia TEJ SAMEJ osi dalej:

  A GLEBOKOSC   -- ziarna wybieramy bramka binarna, nigdy po `blad_odtworzenia`.
                   Rozrzut na naszych 100 ziarnach: 13-21-34. Bierzemy skrajny
                   kwantyl (najglebiej na rozmaitosci modelu).
  B POKOLENIE   -- nasze ziarna leza 102-133 od dzikiego. Nie sprawdzilismy,
                   co jest na 150-250 wzdluz kierunku dekodera. Drugie i trzecie
                   pokolenie leza wlasnie tam.
  K KONTROLA    -- 10 obecnych ziaren z v4, zeby wynik dalo sie odczytac.

Zastrzezenie metodyczne: W18 pokazal, ze `blad_odtworzenia` nie przewiduje
werdyktu Sedziego (d = +0,06). Ale Sedzia jest WYSYCONY -- nie szereguje
niczego powyzej progu. Brak korelacji z Sedzia nie jest dowodem co do
Wyroczni. Ta sama pulapka co przy edycjach gatunkowych.

Przebieg jest ZROWNOLEGLONY: /me podaje 3000 wywolan/min na sedzie, mape
i edycje. Sekwencyjnie ten eksperyment trwa ~12 min, w puli watkow ~1,5 min.

    python eksperymenty/E13_glebokosc/run.py [--losowan 1600] [--watkow 16]
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client, rownolegle  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"
NAZWA = "v14_glebokosc"

POZIOMY = (1, 2)              # poziom 0 dal 0/48 trafien (W21)
ILE_KODOW = (8, 16, 24, 32)   # ile_kodow=4 jest martwe (W21)
OPCJI = 8
N_A, N_B, N_K = 45, 45, 10
CEL = 100                     # ALL100 dzieli zawsze przez 100 -- brak = zero


_licznik = threading.Lock()
_stan = {"n": 0}


def _tik(co: str, co_ile: int = 200) -> None:
    with _licznik:
        _stan["n"] += 1
        n = _stan["n"]
    if n % co_ile == 0:
        print(f"  {co}: {n}", flush=True)


def przesiew(c: Client, dziki: str, budzet: int, watkow: int) -> list[dict]:
    """Losuje kandydatow, przepuszcza przez bramke, mierzy glebokosc.

    Trzy fazy, kazda zrownoleglona: edycje -> bramka Sedziego -> mapa.
    """
    zadania, nr = [], 700_000
    while len(zadania) * OPCJI < budzet:
        for poziom in POZIOMY:
            for ile_kodow in ILE_KODOW:
                nr += 1
                zadania.append((poziom, ile_kodow, nr))
    print(f"  faza 1/3: {len(zadania)} wywolan /edycje "
          f"({len(zadania) * OPCJI} losowan)", flush=True)
    _stan["n"] = 0
    partie = rownolegle(
        lambda z: (z, c.edycje(dziki, poziom=z[0], ile_kodow=z[1],
                               opcji=OPCJI, ziarno=z[2]), _tik("edycje", 20))[:2],
        zadania, watkow=watkow)

    surowe = []
    for wynik in partie:
        if wynik is None:
            continue
        (poziom, ile_kodow, _), e = wynik
        for o in e["opcje"]:
            surowe.append({"sekwencja": o["sekwencja"],
                           "poziom": poziom, "ile_kodow": ile_kodow})
    print(f"  faza 2/3: bramka Sedziego na {len(surowe)} opcjach", flush=True)
    _stan["n"] = 0
    werdykty = rownolegle(
        lambda x: (c.lepsza(dziki, x["sekwencja"]), _tik("bramka"))[0],
        surowe, watkow=watkow, na_blad=False)
    przez = [x for x, w in zip(surowe, werdykty) if w]

    print(f"  faza 3/3: glebokosc dla {len(przez)} kandydatow", flush=True)
    _stan["n"] = 0
    mapy = rownolegle(
        lambda x: (c.mapa(x["sekwencja"], od=0, ile=800), _tik("mapa"))[0],
        przez, watkow=watkow)

    kandydaci = []
    for x, m in zip(przez, mapy):
        if m is None:
            continue
        kandydaci.append({**x,
                          "blad_odtworzenia": m["blad_odtworzenia"],
                          "dystans": S.hamming(dziki, x["sekwencja"])})
    return kandydaci


def pokolenia(c: Client, dziki: str, ziarna: list[F.Rekord],
              ile: int, watkow: int) -> list[dict]:
    """Drugie i trzecie przejscie przez dekoder -- dalej wzdluz kierunku.

    Linie rodowe sa niezalezne, wiec ida rownolegle; wewnatrz linii
    pokolenia musza isc po kolei.
    """
    def linia(arg):
        i, z = arg
        out, biezaca, pokolenie = [], z.seq, 1
        for _ in range(2):
            pokolenie += 1
            try:
                e = c.edycje(biezaca, poziom=2, ile_kodow=16, opcji=4,
                             ziarno=800_000 + i * 10 + pokolenie)
            except Exception:                                # noqa: BLE001
                break
            wybor = next((o["sekwencja"] for o in e["opcje"]
                          if c.lepsza(dziki, o["sekwencja"])), None)
            if wybor is None:
                break
            biezaca = wybor
            m = c.mapa(biezaca, od=0, ile=800)
            out.append({"sekwencja": biezaca, "pokolenie": pokolenie,
                        "blad_odtworzenia": m["blad_odtworzenia"],
                        "dystans": S.hamming(dziki, biezaca)})
        _tik("linie", 10)
        return out

    _stan["n"] = 0
    linie = rownolegle(linia, list(enumerate(ziarna)), watkow=watkow, na_blad=[])
    out = []
    for grupa in linie:
        out.extend(grupa or [])
    return out[:ile]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--losowan", type=int, default=1600)
    ap.add_argument("--watkow", type=int, default=16)
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    ziarna_v4 = F.czytaj(WYJSCIE / "v4.fasta")

    print("=== BLOK A: przesiew na glebokosc ===")
    pula = przesiew(c, dziki, a.losowan, a.watkow)
    pula.sort(key=lambda x: x["blad_odtworzenia"])
    blok_a = pula[:N_A]
    print(f"  przez bramke {len(pula)} z ~{a.losowan}"
          f" ({100*len(pula)/max(a.losowan,1):.1f} %)")
    if pula:
        b = [x["blad_odtworzenia"] for x in pula]
        print(f"  blad_odtworzenia w puli: {min(b)} - {int(st.median(b))} - {max(b)}")
        print(f"  wybrane (najglebsze {len(blok_a)}): "
              f"{blok_a[0]['blad_odtworzenia']} - {blok_a[-1]['blad_odtworzenia']}")

    print("\n=== BLOK B: dalsze pokolenia ===")
    blok_b = pokolenia(c, dziki, ziarna_v4[:40], N_B, a.watkow)
    if blok_b:
        d = [x["dystans"] for x in blok_b]
        print(f"  wariantow {len(blok_b)}, dystans od dzikiego "
              f"{min(d)} - {int(st.median(d))} - {max(d)}")

    rekordy = [F.Rekord(f"A_gleb{x['blad_odtworzenia']:02d}_{i:03d}", x["sekwencja"])
               for i, x in enumerate(blok_a)]
    rekordy += [F.Rekord(f"B_pok{x['pokolenie']}_d{x['dystans']}_{i:03d}", x["sekwencja"])
                for i, x in enumerate(blok_b)]
    rekordy += [F.Rekord(f"K_kontrola_{i:03d}", z.seq)
                for i, z in enumerate(ziarna_v4[:N_K])]

    # Dopelnienie do 100. ALL100 dzieli zawsze przez 100, wiec kazda brakujaca
    # sekwencja wchodzi jako zero -- niedobor w bloku B kosztowalby nas punkty
    # w polu, w ktorym i tak stoimy najgorzej (ranga 6/10 na 2026-08-29 18:39).
    uzyte = {r.seq for r in rekordy}
    dopelniacze = 0
    for x in pula[N_A:]:
        if len(rekordy) >= CEL:
            break
        if x["sekwencja"] in uzyte:
            continue
        uzyte.add(x["sekwencja"])
        dopelniacze += 1
        rekordy.append(F.Rekord(
            f"D_gleb{x['blad_odtworzenia']:02d}_{dopelniacze:03d}", x["sekwencja"]))
    for z in ziarna_v4[N_K:]:
        if len(rekordy) >= CEL:
            break
        if z.seq in uzyte:
            continue
        uzyte.add(z.seq)
        dopelniacze += 1
        rekordy.append(F.Rekord(f"D_ziarno_{dopelniacze:03d}", z.seq))
    if dopelniacze:
        print(f"\n  dopelniono {dopelniacze} sekwencji do {CEL}")

    raport = F.waliduj(rekordy)
    plik = WYJSCIE / f"{NAZWA}.fasta"
    F.zapisz(plik, raport.ok[:CEL])
    print("\n" + raport.podsumowanie())
    print(f"zapisano -> {plik}")

    (TU / "wyniki.json").write_text(json.dumps({
        "eksperyment": "E13_glebokosc", "plik": f"{NAZWA}.fasta",
        "losowan": a.losowan, "przez_bramke": len(pula),
        "dopelniaczy": dopelniacze,
        "blok_A": [{k: v for k, v in x.items() if k != "sekwencja"} for x in blok_a],
        "blok_B": [{k: v for k, v in x.items() if k != "sekwencja"} for x in blok_b],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
