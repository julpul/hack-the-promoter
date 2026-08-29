#!/usr/bin/env python3
"""E15e -- budowa v14_glebokosc_v2 + zestaw cis z PIVOT.md na najlepszej bazie.

Podstawa doboru (zmierzona w E15d, `pokolenia.json`):

    pokolenie 1 (przesiew 1600, wybrane najglebsze)   blad  9 - 17 - 19
    pokolenie 2                                       blad  1 -  5 - 14
    pokolenie 3                                       blad  0 -  2 - 11
    pokolenie 4                                       blad  0 -  2 -  7   <- nasycenie
    pokolenie 5                                       blad  0 -  2 -  8

Glebokosc nasyca sie na pokoleniu 4, a dystans od dzikiego rosnie dalej
(167 -> 181 pz). Bierzemy wiec **pokolenie 4**: cala dostepna glebokosc przy
najmniejszym dystansie, przy ktorym ja dostajemy.

Kazda linia rodowa daje **jedna** sekwencje. Pokolenia 3/4/5 tej samej linii
sa zagniezdzone, wiec wpuszczenie ich razem powtorzyloby blad W11/W22:
sto skorelowanych wariantow to nie sto losowan, a TOP10 jest statystyka
pozycyjna i widzi tylko liczbe NIEZALEZNYCH prob.

Zestaw cis odpowiada na P2 z `E14/PLAN.md` -- czy bloki z `PIVOT.md` dokladaja
cokolwiek na glebokiej bazie. Uzasadnienie kazdego bloku jest teraz liczone
wobec NASZEJ bazy, nie wobec literatury:

    CCAAT   dziki 0, konsensus ziaren 0, tylko 46 % ziaren ma >=1  -> instalujemy
    CreA    dziki 2, konsensus ziaren 4  -> dekoder DOKLADA represor, rozbijamy
    XBS     dziki 3, konsensus ziaren 1  -> dekoder USUWA aktywator, przywracamy
    rdzen   751-800 nietkniety (W26: log-odds dzikiego w 52. percentylu)
    poz 798 A zostaje -- dekoder wstawia ja w 100/100, zgodnie z konserwacja
              w stu naturalnych promotorach (W25: IC 0,525, A w 62/100)

    python eksperymenty/E15_konsensus/buduj.py [--linii 110] [--watkow 16]
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client, rownolegle  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pokolenia as _pok  # noqa: E402
from pokolenia import linia  # noqa: E402

# Pokolenie 4 to nasycenie glebokosci (E15d), wiec nie ciagniemy linii do 5 --
# to sam koszt czasu i dystansu bez zysku.
_pok.POKOLEN = 4

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"

CEL = 100
POKOLENIE_DOCELOWE = 4
RDZEN_OD = 751          # 1-based; rdzenia -50..0 nie ruszamy

# Pas, w ktorym naturalne promotory Trichoderma trzymaja CCAAT: -500..-200,
# czyli pozycje 300-600 przy TSS = 800. Mediana naturalnych -388 -> poz. 412.
CCAAT_POZYCJE = (412, 470, 528, 586)
CCAAT = "CCAAT"

# Rdzen XBS z xyn1 (odwrocone powtorzenie GGCTAA rozdzielone 10 pz).
XBS_IR = "GGCTAAATGCGACATCTTAGCC"
XBS_POZYCJA = 330       # -470, powyzej pasa CCAAT, zgodnie z PIVOT 4


def rozbij_crea(seq: str) -> tuple[str, int]:
    """Rozbija miejsca CreA (SYGGRG) jednym podstawieniem kazde.

    Zmieniamy srodkowe G na A: SYGGRG -> SYGARG lamie rdzen wiazania Cre1,
    a jest to jedna zasada. Rdzenia 751-800 nie ruszamy.
    """
    out, ile = list(seq), 0
    for p in S.znajdz_iupac(seq, "SYGGRG"):
        i = p - 1 + 3                       # czwarta pozycja motywu (G)
        if i + 1 > RDZEN_OD:
            continue
        if out[i] == "G":
            out[i] = "A"
            ile += 1
    return "".join(out), ile


def wstaw_ccaat(seq: str, pozycje) -> tuple[str, int]:
    out, ile = seq, 0
    for p in pozycje:
        if p + len(CCAAT) - 1 > RDZEN_OD:
            continue
        out = S.wstaw(out, CCAAT, p)
        ile += 1
    return out, ile


def wstaw_xbs(seq: str) -> tuple[str, int]:
    if XBS_POZYCJA + len(XBS_IR) - 1 > RDZEN_OD:
        return seq, 0
    return S.wstaw(seq, XBS_IR, XBS_POZYCJA), 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--linii", type=int, default=110)
    ap.add_argument("--watkow", type=int, default=16)
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    t0 = time.time()

    # Startujemy z v4 -- E15d pokazal, ze glebokosc startu nie ma znaczenia
    # (ramie plytkie i glebokie zbiegaja do tej samej mediany 2 na pokoleniu 4),
    # a v4 ma 100 potwierdzonych niezaleznych skupien (W24).
    v4 = F.czytaj(WYJSCIE / "v4.fasta")
    starty = [(r.seq, "v2", i) for i, r in enumerate(v4[:a.linii])]
    if len(starty) < a.linii:
        v14 = [r for r in F.czytaj(WYJSCIE / "v14_glebokosc.fasta")
               if r.nazwa.startswith("A_gleb")]
        starty += [(r.seq, "v2", 5000 + i)
                   for i, r in enumerate(v14[:a.linii - len(starty)])]

    print(f"faza 1: {len(starty)} linii rodowych do pokolenia {POKOLENIE_DOCELOWE}",
          flush=True)
    wyniki = rownolegle(lambda z: linia(c, dziki, z[0], z[1], z[2]),
                        starty, watkow=a.watkow, na_blad=[])

    # Jedna sekwencja na linie: docelowe pokolenie, a jesli linia wygasla
    # wczesniej -- najglebsze, co przezylo. Nigdy dwie z tej samej linii.
    najlepsze = []
    for grupa in wyniki:
        if not grupa:
            continue
        docelowe = [x for x in grupa if x["pokolenie"] == POKOLENIE_DOCELOWE]
        wybor = (docelowe or sorted(grupa, key=lambda x: x["blad_odtworzenia"]))[0]
        najlepsze.append(wybor)
    najlepsze.sort(key=lambda x: x["blad_odtworzenia"])
    baza = najlepsze[:CEL]
    print(f"  linii z wynikiem: {len(najlepsze)}, biore {len(baza)}"
          f", {time.time() - t0:.0f}s")
    if baza:
        b = [x["blad_odtworzenia"] for x in baza]
        d = [x["dystans"] for x in baza]
        print(f"  blad_odtworzenia: {min(b)} - {st.median(b):.0f} - {max(b)}")
        print(f"  dystans od dzik : {min(d)} - {st.median(d):.0f} - {max(d)}")
        from collections import Counter
        print(f"  pokolenia       : "
              f"{dict(sorted(Counter(x['pokolenie'] for x in baza).items()))}")

    # ---------- zestaw 1: czysta glebokosc pokoleniowa ----------
    rek_v2 = [F.Rekord(f"P{x['pokolenie']}_b{x['blad_odtworzenia']:02d}_"
                       f"d{x['dystans']}_{i:03d}", x["sekwencja"])
              for i, x in enumerate(baza)]

    # ---------- zestaw 2: te same bazy + bloki cis z PIVOT ----------
    print("\nfaza 2: instalacja blokow cis na tej samej bazie", flush=True)
    cis, licznik = [], {"ccaat": [], "crea": [], "xbs": 0}
    for i, x in enumerate(baza):
        s = x["sekwencja"]
        s, n_crea = rozbij_crea(s)
        s, n_cc = wstaw_ccaat(s, CCAAT_POZYCJE)
        s, n_xbs = wstaw_xbs(s)
        licznik["ccaat"].append(n_cc)
        licznik["crea"].append(n_crea)
        licznik["xbs"] += n_xbs
        cis.append({**x, "sekwencja_cis": s,
                    "zmian_cis": S.hamming(x["sekwencja"], s)})
    zm = [x["zmian_cis"] for x in cis]
    print(f"  CCAAT wstawionych/sekw : {st.median(licznik['ccaat']):.0f}")
    print(f"  CreA rozbitych/sekw    : {min(licznik['crea'])} - "
          f"{st.median(licznik['crea']):.0f} - {max(licznik['crea'])}")
    print(f"  IR-XBS wstawionych     : {licznik['xbs']}/{len(cis)}")
    print(f"  zmian na sekwencje     : {min(zm)} - {st.median(zm):.0f} - {max(zm)} pz")

    # Ile glebokosci kosztuje biologia -- to jest odpowiedz na P2 z E14.
    print("\nfaza 3: koszt blokow cis w glebokosci i na bramce", flush=True)
    proba = cis[:40]
    mapy = rownolegle(lambda x: c.mapa(x["sekwencja_cis"], 0, 800),
                      proba, watkow=a.watkow)
    bram = rownolegle(lambda x: c.lepsza(dziki, x["sekwencja_cis"]),
                      proba, watkow=a.watkow, na_blad=None)
    przed = [x["blad_odtworzenia"] for x, m in zip(proba, mapy) if m]
    po = [m["blad_odtworzenia"] for m in mapy if m]
    przez = sum(1 for b in bram if b)
    print(f"  n = {len(po)}")
    print(f"  blad PRZED blokami : {min(przed)} - {st.median(przed):.1f} - {max(przed)}")
    print(f"  blad PO blokach    : {min(po)} - {st.median(po):.1f} - {max(po)}")
    print(f"  koszt (mediana)    : +{st.median(po) - st.median(przed):.1f}")
    print(f"  bramka Sedziego    : {przez}/{len(bram)} przechodzi")

    rek_cis = [F.Rekord(f"C{x['pokolenie']}_b{x['blad_odtworzenia']:02d}_"
                        f"cis{x['zmian_cis']}_{i:03d}", x["sekwencja_cis"])
               for i, x in enumerate(cis)]

    for nazwa, rekordy in (("v14_glebokosc_v2", rek_v2),
                           ("v18_pokolenia_cis", rek_cis)):
        raport = F.waliduj(rekordy)
        plik = WYJSCIE / f"{nazwa}.fasta"
        F.zapisz(plik, raport.ok[:CEL])
        print(f"\n--- {nazwa} ---")
        print(raport.podsumowanie())
        print(f"zapisano -> {plik}")

    (TU / "buduj.json").write_text(json.dumps({
        "linii": len(starty), "pokolenie_docelowe": POKOLENIE_DOCELOWE,
        "sekund": round(time.time() - t0),
        "baza": [{k: v for k, v in x.items() if k != "sekwencja"} for x in baza],
        "koszt_cis": {"przed_mediana": st.median(przed) if przed else None,
                      "po_mediana": st.median(po) if po else None,
                      "bramka": f"{przez}/{len(bram)}"},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
