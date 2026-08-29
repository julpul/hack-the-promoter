#!/usr/bin/env python3
"""E15f -- jak daleko siega os pokolen. Pokolenia 6-8.

Dwa fakty ustalone znacznikiem w /ranking (serwer trzyma NAJLEPSZE po surowym
TOP10, nie ostatnie -- potwierdzone tym, ze v18 wgrany o 17:50 nie ruszyl
znacznika 17:34:45):

    v2 (pokolenie 4)  >  v14 (mieszanka pok. 1 i 2/3)    znacznik SIE RUSZYL
    v18 (v2 + bloki cis)  <  v2                          znacznik NIE drgnal

Czyli: os pokolen dziala, bloki cis szkodza. Zamykamy CCAAT/XBS (v8, v12,
v13, v18 -- cztery pomiary) i pchamy jedyna os z potwierdzona wygrana.

`blad_odtworzenia` nasyca sie na pokoleniu 4 (mediana 2, minimum 0), ale
dystans od dzikiego rosnie dalej: 167 -> 181 na pokoleniu 5. Skoro glebokosc
juz nie rosnie, a v2 mimo to wygral, to znaczy, ze zysk moze pochodzic
z DYSTANSU wzdluz kierunku dekodera, a nie z glebokosci. Pokolenia 6-8 leza
na 195-230 pz i sa jedynym miejscem, gdzie te dwie hipotezy sie rozjezdzaja.

    python eksperymenty/E15_konsensus/dalej.py [--linii 140] [--watkow 24]
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client, rownolegle  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pokolenia as _pok  # noqa: E402
from pokolenia import linia  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"
CEL = 100


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--linii", type=int, default=140)
    ap.add_argument("--watkow", type=int, default=24)
    ap.add_argument("--do-pokolenia", type=int, default=8)
    ap.add_argument("--nazwa", default="v19_pokolenie8")
    a = ap.parse_args()

    _pok.POKOLEN = a.do_pokolenia
    c = Client.from_env()
    dziki = c.dziki_seq()
    t0 = time.time()

    v4 = F.czytaj(WYJSCIE / "v4.fasta")
    starty = [(r.seq, "dalej", i) for i, r in enumerate(v4[:a.linii])]
    if len(starty) < a.linii:
        v14 = [r for r in F.czytaj(WYJSCIE / "v14_glebokosc.fasta")
               if r.nazwa.startswith("A_gleb")]
        starty += [(r.seq, "dalej", 7000 + i)
                   for i, r in enumerate(v14[:a.linii - len(starty)])]

    print(f"{len(starty)} linii do pokolenia {a.do_pokolenia}", flush=True)
    wyniki = rownolegle(lambda z: linia(c, dziki, z[0], z[1], z[2]),
                        starty, watkow=a.watkow, na_blad=[])
    pula = [x for g in wyniki for x in (g or [])]
    print(f"\nzebrano {len(pula)} wariantow, {time.time() - t0:.0f}s\n")

    print(f"{'pok':>4} {'n':>4} {'blad: min-med-max':>22} {'dystans: med':>13}")
    tab = []
    for p in range(2, a.do_pokolenia + 1):
        g = [x for x in pula if x["pokolenie"] == p]
        if not g:
            continue
        b = [x["blad_odtworzenia"] for x in g]
        d = [x["dystans"] for x in g]
        tab.append({"pokolenie": p, "n": len(g), "blad_min": min(b),
                    "blad_mediana": st.median(b), "blad_max": max(b),
                    "dystans_mediana": st.median(d)})
        print(f"{p:>4} {len(g):>4} {min(b):>8} {st.median(b):>6.1f} {max(b):>6}"
              f" {st.median(d):>13.0f}")

    # Jedna sekwencja na linie -- najdalsze przezyle pokolenie.
    najdalsze = {}
    for x in pula:
        k = x["linia"]
        if k not in najdalsze or x["pokolenie"] > najdalsze[k]["pokolenie"]:
            najdalsze[k] = x
    baza = sorted(najdalsze.values(),
                  key=lambda x: (-x["pokolenie"], x["blad_odtworzenia"]))[:CEL]
    print(f"\nlinii z wynikiem {len(najdalsze)}, biore {len(baza)}")
    print(f"  pokolenia w pliku: {dict(sorted(Counter(x['pokolenie'] for x in baza).items()))}")
    b = [x["blad_odtworzenia"] for x in baza]
    d = [x["dystans"] for x in baza]
    print(f"  blad    : {min(b)} - {st.median(b):.0f} - {max(b)}")
    print(f"  dystans : {min(d)} - {st.median(d):.0f} - {max(d)}")

    rek = [F.Rekord(f"P{x['pokolenie']}_b{x['blad_odtworzenia']:02d}"
                    f"_d{x['dystans']}_{i:03d}", x["sekwencja"])
           for i, x in enumerate(baza)]
    raport = F.waliduj(rek)
    plik = WYJSCIE / f"{a.nazwa}.fasta"
    F.zapisz(plik, raport.ok[:CEL])
    print("\n" + raport.podsumowanie())
    print(f"zapisano -> {plik}")

    (TU / "dalej.json").write_text(json.dumps({
        "do_pokolenia": a.do_pokolenia, "linii": len(starty),
        "sekund": round(time.time() - t0), "tabela": tab,
        "baza": [{k: v for k, v in x.items() if k != "sekwencja"} for x in baza],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
