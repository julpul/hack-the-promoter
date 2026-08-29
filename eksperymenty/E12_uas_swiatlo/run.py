#!/usr/bin/env python3
"""E12 -- architektura UAS + zniesienie represji swietlnej.

Dwie przeslanki, ktorych nie mielismy wczesniej:

1. LITERATURA (Aspergillus niger, T. reesei): sile syntetycznych promotorow
   grzybowych stroi sie **tandemowymi powtorzeniami UAS** dolaczonymi do rdzenia,
   a nie pojedynczymi miejscami rozrzuconymi po sekwencji. Nasz v8 wstawial
   CCAAT **rozproszone** -- architektury tandemowej nikt nie testowal.

2. LITERATURA (T. atroviride): **swiatlo HAMUJE biosynteze 6PP**, najwyzsza
   produkcja w ciemnosci; sygnal idzie przez kompleks BLR (homolog White Collar).
   NASZ POMIAR: dziki ma C-box (GATCGA, kanoniczne miejsce WCC) na -523 oraz
   dwa powtorzenia GATN na -523 i -197. Mediana w 100 naturalnych promotorach
   dla obu wynosi **0**. Czyli `pks1` ma elementy swietlne PONAD norme rodzaju.

   Hipoteza: rozbicie ich = zniesienie represji swietlnej = wyzsza ekspresja.
   To jest usuniecie hamulca, a nie dodanie gazu -- ten sam typ interwencji
   co CreA, ale poparty publikacja o TYM genie i TYM gatunku.

Baza pozostaje bez zmian (W30: kazda zmiana bazy pogarsza wynik) -- ziarna
dekodera z v4. Cztery bloki po 25, z blokiem B jako kontrola wewnetrzna
(replikacja v8, naszego najlepszego zgloszenia).

    python eksperymenty/E12_uas_swiatlo/run.py
"""

from __future__ import annotations

import json
import random
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
NAZWA = "v13_uas_swiatlo"

OKNO_UAS = (294, 612)      # empiryczne kwartyle CCAAT w 100 naturalnych: -506..-188
ODSTEP_TANDEM = 5          # przerywnik miedzy powtorzeniami w bloku UAS
LRE = ["GATCGA", "GATNGATN"]   # elementy swietlne (WCC/BLR)
CREA = "SYGGRG"


def rozbij(s: str, wzor: str) -> tuple[str, int]:
    """Rozbija wszystkie wystapienia motywu jednym podstawieniem na miejsce."""
    ile = 0
    for _ in range(10):
        traf = S.znajdz_iupac(s, wzor)
        if not traf:
            break
        p = traf[0]
        srodek = p - 1 + len(wzor) // 2
        for z in "ACGT":
            if z == s[srodek]:
                continue
            kand = s[:srodek] + z + s[srodek + 1:]
            if len(S.znajdz_iupac(kand, wzor)) < len(traf):
                s, ile = kand, ile + 1
                break
        else:
            break
    return s, ile


def blok_uas(s: str, powtorzen: int, r: random.Random) -> str:
    """Tandemowy blok UAS: CCAAT x n z krotkimi przerywnikami, w jednym miejscu."""
    dlugosc = powtorzen * 5 + (powtorzen - 1) * ODSTEP_TANDEM
    start = r.randint(OKNO_UAS[0], OKNO_UAS[1] - dlugosc)
    p = start
    for _ in range(powtorzen):
        s = S.wstaw(s, "CCAAT", p)
        p += 5 + ODSTEP_TANDEM
    return s


def ccaat_rozproszone(s: str, ile: int, r: random.Random) -> str:
    """Architektura z v8: pojedyncze CCAAT rozrzucone po oknie."""
    uzyte: list[int] = []
    for _ in range(ile):
        for _proba in range(30):
            p = r.randint(*OKNO_UAS)
            if all(abs(p - u) > 30 for u in uzyte):
                uzyte.append(p)
                s = S.wstaw(s, "CCAAT", p)
                break
    return s


def zbuduj() -> tuple[list[F.Rekord], dict]:
    ziarna = F.czytaj(WYJSCIE / "v4.fasta")
    r = random.Random(612)
    out, staty = [], {"lre_rozbitych": [], "crea_rozbitych": []}

    for i, z in enumerate(ziarna[:100]):
        blok = i // 25            # 0..3
        s = z.seq
        if blok == 0:             # A: tandemowy blok UAS
            s = blok_uas(s, 2 + (i % 4), r)
            etyk = f"A_tandem{2 + (i % 4)}"
        elif blok == 1:           # B: KONTROLA -- rozproszone CCAAT (jak v8)
            s = ccaat_rozproszone(s, 1 + (i % 4), r)
            etyk = f"B_rozprosz{1 + (i % 4)}"
        elif blok == 2:           # C: tandem + zniesienie represji swietlnej
            s = blok_uas(s, 2 + (i % 3), r)
            n = 0
            for w in LRE:
                s, k = rozbij(s, w)
                n += k
            staty["lre_rozbitych"].append(n)
            etyk = f"C_tandem_swiatlo{n}"
        else:                     # D: tandem + zniesienie represji weglowej
            s = blok_uas(s, 2 + (i % 3), r)
            s, k = rozbij(s, CREA)
            staty["crea_rozbitych"].append(k)
            etyk = f"D_tandem_creA{k}"
        out.append(F.Rekord(f"{etyk}_{i:03d}", s))
    return out, staty


def main() -> int:
    c = Client.from_env()
    dziki = c.dziki_seq()
    rekordy, staty = zbuduj()
    raport = F.waliduj(rekordy)
    plik = WYJSCIE / f"{NAZWA}.fasta"
    F.zapisz(plik, raport.ok[:100])

    seqs = [x.seq for x in raport.ok[:100]]
    r = random.Random(0)
    prob = r.sample(raport.ok[:100], 20)
    bramka = sum(1 for x in prob if c.lepsza(dziki, x.seq))

    bloki: dict[str, dict] = {}
    for x in raport.ok[:100]:
        b = x.nazwa[0]
        d = bloki.setdefault(b, {"n": 0, "ccaat": [], "lre": [], "crea": []})
        d["n"] += 1
        d["ccaat"].append(len(S.znajdz_iupac(x.seq, "CCAAT")))
        d["lre"].append(sum(len(S.znajdz_iupac(x.seq, w)) for w in LRE))
        d["crea"].append(len(S.znajdz_iupac(x.seq, CREA)))

    print(raport.podsumowanie())
    print(f"\nbramka Sedziego: {bramka}/20")
    print(f"dystans od dzikiego: {min(S.hamming(dziki,s) for s in seqs)}"
          f"/{int(st.median([S.hamming(dziki,s) for s in seqs]))}"
          f"/{max(S.hamming(dziki,s) for s in seqs)}")
    print(f"\n{'blok':<6}{'n':>4}{'CCAAT sr':>10}{'LRE sr':>9}{'CreA sr':>9}")
    for b in sorted(bloki):
        d = bloki[b]
        print(f"{b:<6}{d['n']:>4}{st.mean(d['ccaat']):>10.1f}"
              f"{st.mean(d['lre']):>9.2f}{st.mean(d['crea']):>9.2f}")
    print(f"\nzapisano -> {plik}")

    (TU / "wyniki.json").write_text(json.dumps(
        {"eksperyment": "E12_uas_swiatlo", "plik": f"{NAZWA}.fasta",
         "bramka": f"{bramka}/20",
         "bloki": {b: {"n": d["n"], "ccaat_sr": round(st.mean(d["ccaat"]), 2),
                       "lre_sr": round(st.mean(d["lre"]), 2),
                       "crea_sr": round(st.mean(d["crea"]), 2)}
                   for b, d in bloki.items()}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
