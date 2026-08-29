#!/usr/bin/env python3
"""Pomiar gotowego portfela PRZED zuzyciem okna 5 minut.

Bramka Sedziego jest darmowa i powtarzalna (E01: 8/8 albo 0/8 na siedmiu parach),
a okno /wgraj jest jedno na piec minut. Nie ma powodu, zeby dowiadywac sie
o skladzie pliku dopiero z rankingu.

Zwraca odsetek sekwencji przechodzacych bramke -- w rozbiciu na bloki, bo
etykiety niosa pochodzenie (regula 5 z README).

    python eksperymenty/E05_portfel/zmierz.py runs/julian/v2.fasta [...]
"""

from __future__ import annotations

import argparse
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import klient, metryki as M, zapisz  # noqa: E402
from hyppe import fasta as F, seq as S  # noqa: E402

TU = Path(__file__).resolve().parent


def blok(nazwa: str) -> str:
    """Etykieta -> blok. `b07_rdzen_dz_777` -> `b07`, `E04_A1B0C1D0_r00` -> `E04`."""
    return nazwa.split("_")[0]


def zmierz(c, dziki: str, sciezka: Path, bez_mapy: bool = False) -> dict:
    rek = F.czytaj(sciezka)
    print(f"\n=== {sciezka}  ({len(rek)} sekwencji) ===")
    wyniki = []
    for i, r in enumerate(rek, 1):
        w = {"nazwa": r.nazwa, "blok": blok(r.nazwa),
             "bije_dzikiego": c.lepsza(dziki, r.seq),
             "dystans_od_dzikiego": S.hamming(dziki, r.seq),
             "gc": round(S.gc(r.seq), 4)}
        if not bez_mapy:
            m = M.metryki_mapy(c.mapa(r.seq))
            w |= {k: m.get(k) for k in
                  ("blad_odtworzenia", "zmian_pod_gatunek", "masa_rdzenia", "srodek_masy")}
        wyniki.append(w)
        if i % 25 == 0:
            print(f"  [{i:3d}/{len(rek)}] przechodzi bramke: "
                  f"{sum(x['bije_dzikiego'] for x in wyniki)}")

    wyg = sum(x["bije_dzikiego"] for x in wyniki)
    print(f"\n  BRAMKA SEDZIEGO: {wyg}/{len(wyniki)} ({wyg / len(wyniki):.0%})")
    print(f"  {'blok':<10}{'n':>4}{'przechodzi':>13}{'blad_odtw':>12}{'dyst':>7}")
    for b in sorted({x["blok"] for x in wyniki}):
        g = [x for x in wyniki if x["blok"] == b]
        w = sum(x["bije_dzikiego"] for x in g)
        bo = [x["blad_odtworzenia"] for x in g if x.get("blad_odtworzenia") is not None]
        print(f"  {b:<10}{len(g):>4}{f'{w}/{len(g)} ({w / len(g):.0%})':>13}"
              f"{(f'{st.median(bo):.0f}' if bo else '-'):>12}"
              f"{st.median([x['dystans_od_dzikiego'] for x in g]):>7.0f}")
    return {"plik": str(sciezka), "n": len(wyniki), "przechodzi_bramke": wyg,
            "sekwencje": wyniki}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pliki", nargs="+")
    ap.add_argument("--bez-mapy", action="store_true", help="tylko bramka, bez /mapa")
    args = ap.parse_args()

    c = klient()
    dziki = c.dziki_seq()
    raporty = [zmierz(c, dziki, Path(p), args.bez_mapy) for p in args.pliki]

    if len(raporty) > 1:
        print("\n=== PORoWNANIE ===")
        for r in raporty:
            print(f"  {r['plik']:<40} {r['przechodzi_bramke']:>3}/{r['n']} "
                  f"({r['przechodzi_bramke'] / r['n']:.0%})")

    p = zapisz(TU / "pomiar_portfela.json",
               {"eksperyment": "E05_pomiar_portfela", "raporty": raporty})
    print(f"\nzapisano: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
