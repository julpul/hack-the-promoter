#!/usr/bin/env python3
"""E15b -- czy glebokosc rosnie w strone konsensusu? Offline, 0 wywolan API.

Analiza konsensusu dala wynik odwrotny do przewidywanego: 100 ziaren NIE
uzgadnia sie do dzikiego. Konsensus lezy 91 pz od dzikiego, a w kazdej z tych
91 kolumn dziki jest w MNIEJSZOSCI (udzial < 50 %, czesto 0,00). Czyli zmiany
dekodera nie sa rozrzucone losowo -- sa w duzej mierze te same za kazdym razem.

Rozklad sie rozpada na dwie skladowe:

    ziarno = konsensus (skladowa systematyczna) + ~51 pz wlasnego szumu

Jesli `blad_odtworzenia` mierzy odleglosc od rozmaitosci modelu, a konsensus
jest srodkiem tej rozmaitosci, to **ziarna blizsze konsensusu powinny byc
glebsze**. Nazwy w `v14_glebokosc.fasta` niosa zmierzona glebokosc bloku A
(`A_gleb09_000` -> 9), wiec te korelacje da sie policzyc BEZ wywolan API.

To jest test falsyfikowalny i darmowy. Jesli wyjdzie zero, hipoteza
"konsensus = najglebszy punkt" pada zanim wydamy cokolwiek na /mapa.

    python eksperymenty/E15_konsensus/korelacja.py
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    licz = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    mian = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return licz / mian if mian else 0.0


def spearman(xs: list[float], ys: list[float]) -> float:
    def rangi(v):
        porzadek = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(porzadek):
            j = i
            while j + 1 < len(porzadek) and v[porzadek[j + 1]] == v[porzadek[i]]:
                j += 1
            sr = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[porzadek[k]] = sr
            i = j + 1
        return r
    return pearson(rangi(xs), rangi(ys))


def main() -> int:
    dane = json.loads((TU / "konsensus.json").read_text(encoding="utf-8"))
    kon = dane["konsensus"]
    dziki = F.czytaj(REPO / "data" / "dziki.fasta")[0].seq.upper()
    rek = F.czytaj(REPO / "runs" / "julian" / "v14_glebokosc.fasta")

    # Blok A niesie zmierzona glebokosc w nazwie: A_gleb09_000 -> 9.
    proby = []
    for r in rek:
        if not r.nazwa.startswith("A_gleb"):
            continue
        glebokosc = int(r.nazwa.split("_")[1][4:])
        proby.append({
            "nazwa": r.nazwa,
            "blad_odtworzenia": glebokosc,
            "do_konsensusu": S.hamming(kon, r.seq.upper()),
            "do_dzikiego": S.hamming(dziki, r.seq.upper()),
        })

    print("=" * 72)
    print("CZY ZIARNA BLIZSZE KONSENSUSU SA GLEBSZE?")
    print("=" * 72)
    print(f"proba: blok A, n = {len(proby)} (glebokosc zmierzona /mapa w E13)\n")

    g = [p["blad_odtworzenia"] for p in proby]
    dk = [p["do_konsensusu"] for p in proby]
    dd = [p["do_dzikiego"] for p in proby]

    print(f"blad_odtworzenia   : {min(g)} - {st.median(g):.0f} - {max(g)}")
    print(f"dystans do konsens.: {min(dk)} - {st.median(dk):.0f} - {max(dk)}")
    print(f"dystans do dzikiego: {min(dd)} - {st.median(dd):.0f} - {max(dd)}")

    print(f"\n{'para':<38} {'Pearson':>9} {'Spearman':>9}")
    print(f"{'glebokosc ~ dystans do KONSENSUSU':<38} "
          f"{pearson(dk, g):>9.3f} {spearman(dk, g):>9.3f}   <- test")
    print(f"{'glebokosc ~ dystans do DZIKIEGO':<38} "
          f"{pearson(dd, g):>9.3f} {spearman(dd, g):>9.3f}   <- kontrola")

    # Podzial na tercyle dystansu do konsensusu -- odporne na ksztalt zaleznosci.
    proby.sort(key=lambda p: p["do_konsensusu"])
    t = len(proby) // 3
    print(f"\n{'tercyl dystansu do konsensusu':<34} {'n':>3} "
          f"{'dyst':>6} {'glebokosc (mediana)':>20}")
    for etyk, grupa in (("blizej konsensusu", proby[:t]),
                        ("srodek", proby[t:2 * t]),
                        ("dalej od konsensusu", proby[2 * t:])):
        gg = [p["blad_odtworzenia"] for p in grupa]
        dd2 = [p["do_konsensusu"] for p in grupa]
        print(f"{etyk:<34} {len(grupa):>3} {st.median(dd2):>6.0f}"
              f" {st.median(gg):>20.1f}")

    print("\nodczyt:")
    print("  korelacja DODATNIA (blizej konsensusu = nizszy blad = glebiej)")
    print("  potwierdza, ze konsensus jest srodkiem rozmaitosci.")
    print("  zero -> hipoteza pada i nie warto mierzyc konsensusu.")

    (TU / "korelacja.json").write_text(json.dumps({
        "n": len(proby),
        "pearson_konsensus": round(pearson(dk, g), 4),
        "spearman_konsensus": round(spearman(dk, g), 4),
        "pearson_dziki": round(pearson(dd, g), 4),
        "spearman_dziki": round(spearman(dd, g), 4),
        "proby": proby,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
