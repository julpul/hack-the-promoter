#!/usr/bin/env python3
"""E11 -- czy trzy drogi na plateau sie SUMUJA?

Po W25-W27 wiemy, ze do plateau (TOP10 poz. 4) prowadza co najmniej trzy
niezalezne drogi, kazda testowana osobno:

    dziki                     5,0 pkt   (linia bazowa, B0)
    + CCAAT (15 pz)          13,0 pkt   (v8)
    + ziarno dekodera        14,0 pkt   (v4)

W12 ustalil, ze zbiory pozycji tych hipotez sa ROZLACZNE, wiec edycje sie nie
znosza. Nikt nie sprawdzil, czy zysk sie kumuluje.

Portfel jest GRADIENTEM intensywnosci, a nie jednym ustawieniem: jesli lekka
kombinacja jest lepsza od ciezkiej (albo odwrotnie), TOP10 wylowi wlasciwy
koniec skali. Bez gradientu jedno zle dobrane natezenie zakopalo by hipoteze.

    python eksperymenty/E11_kombinacja/run.py
"""

from __future__ import annotations

import json
import random
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"
CEL = 100

# Okno CCAAT z empirycznego rozkladu w 100 naturalnych promotorach:
# kwartyle -506..-188 od TSS, czyli pozycje 294-612.
OKNO_CCAAT = (294, 612)
# Trakty poli(dA:dT) do regionu proksymalnego (NFR lezy tuz przed TSS),
# rozlacznie z oknem CCAAT, zeby edycje sie nie nadpisywaly.
OKNO_TRAKTOW = (620, 770)
ODSTEP = 25          # minimalny odstep miedzy wstawkami


def trakty(s: str, minlen: int = 6) -> list[tuple[int, int]]:
    return [(m.start() + 1, len(m.group()))
            for m in re.finditer(r"A{%d,}|T{%d,}" % (minlen, minlen), s)]


def wstaw_bez_kolizji(s: str, motyw: str, okno: tuple[int, int],
                      zajete: list[tuple[int, int]], r: random.Random) -> str:
    """Wstawia motyw w losowym miejscu okna, omijajac juz zajete odcinki."""
    od, do = okno
    for _ in range(40):
        p = r.randint(od, do - len(motyw))
        if all(p + len(motyw) + ODSTEP < a or p > b + ODSTEP for a, b in zajete):
            zajete.append((p, p + len(motyw) - 1))
            return S.wstaw(s, motyw, p)
    return s


def zbuduj(dziki: str) -> list[F.Rekord]:
    zrodlo = WYJSCIE / "v4.fasta"
    if not zrodlo.exists():
        raise SystemExit(f"brak {zrodlo}")
    ziarna = F.czytaj(zrodlo)
    r = random.Random(2026)
    out = []

    for i, z in enumerate(ziarna[:CEL]):
        # GRADIENT wazony wg W28: os CCAAT jest silna (+8,0 nad baza), os
        # traktow slaba i szkodliwa dla sredniej (+3,0, ALL100 bez zmiany).
        # Stad CCAAT rozlozone na calej puli, trakty tylko w 25 sekwencjach
        # i w mniejszym natezeniu -- jako zaklad mniejszosciowy, nie domyslny.
        n_ccaat = 1 + (i % 4)         # 1..4 boksow CCAAT (0 nie ma sensu -- W28)
        n_traktow = (i % 8) - 5 if i % 8 >= 6 else 0   # 1..2 trakty w 25 % puli
        s = z.seq
        zajete: list[tuple[int, int]] = []

        for _ in range(n_ccaat):
            s = wstaw_bez_kolizji(s, "CCAAT", OKNO_CCAAT, zajete, r)
        for _ in range(n_traktow):
            dl = r.randint(10, 20)
            s = wstaw_bez_kolizji(s, r.choice("AT") * dl, OKNO_TRAKTOW, zajete, r)

        out.append(F.Rekord(
            f"K_{i:03d}_z{z.nazwa[1:4]}_c{n_ccaat}_t{n_traktow}", s))
    return out


def main() -> int:
    c = Client.from_env()
    dziki = c.dziki_seq()
    rekordy = zbuduj(dziki)
    raport = F.waliduj(rekordy)
    sciezka = WYJSCIE / "v12_kombinacja.fasta"
    F.zapisz(sciezka, raport.ok[:CEL])

    seqs = [x.seq for x in raport.ok[:CEL]]
    r = random.Random(0)
    prob = r.sample(raport.ok[:CEL], 20)
    bramka = sum(1 for x in prob if c.lepsza(dziki, x.seq))

    # ile sekwencji ma ile skladnikow -- kontrola gradientu
    rozklad: dict[str, int] = {}
    for x in raport.ok[:CEL]:
        klucz = x.nazwa.split("_", 3)[-1]
        rozklad[klucz] = rozklad.get(klucz, 0) + 1

    print(raport.podsumowanie())
    print(f"\ndystans od dzikiego : {min(S.hamming(dziki,s) for s in seqs)}"
          f" / {int(st.median([S.hamming(dziki,s) for s in seqs]))}"
          f" / {max(S.hamming(dziki,s) for s in seqs)}")
    print(f"GC                  : {min(S.gc(s) for s in seqs):.1%}"
          f" – {max(S.gc(s) for s in seqs):.1%}")
    print(f"traktow poli(dA:dT) : {min(len(trakty(s)) for s in seqs)}"
          f" – {max(len(trakty(s)) for s in seqs)}")
    print(f"boksow CCAAT        : {min(len(S.znajdz_iupac(s,'CCAAT')) for s in seqs)}"
          f" – {max(len(S.znajdz_iupac(s,'CCAAT')) for s in seqs)}")
    print(f"bramka Sedziego     : {bramka}/20")
    print(f"\ngradient (c=CCAAT, t=trakty), po ile sekwencji:")
    for k in sorted(rozklad):
        print(f"   {k}: {rozklad[k]}")
    print(f"\nzapisano -> {sciezka}")

    (TU / "wyniki.json").write_text(json.dumps({
        "eksperyment": "E11_kombinacja", "plik": str(sciezka.name),
        "bramka": f"{bramka}/20", "gradient": rozklad}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
