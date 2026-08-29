#!/usr/bin/env python3
"""E14 -- piec wariantow z `PIVOT.md`, kazdy jako osobne zgloszenie.

Budowane offline (instalacja motywu to podstawienie, nie zapytanie), wiec
caly zestaw powstaje w sekundy i mozna go wgrywac co 5 min bez czekania
na API.

Podklad: nie naturalny promotor, tylko nasz najlepszy plik `v14`. Powod
w `PLAN.md` 0.1 -- naturalne DNA przegralo trzy razy (`v6`, `v11` = 4,0
przy linii bazowej 5,0). Wariant `w19` trzyma sie mimo to pivota doslownie
(podklad naturalny), zeby ta hipoteza dostala wlasny pomiar zamiast
zalozenia.

Co mowia nasze trzy ostatnie zgloszenia:

    v14  45 glebokich + 45 pokolen (dystans 123-171) + 10 kontroli  14,0
    v15  100 x najglebsze, jedna rodzina                            12,0
    v16  jak v14, ale pokolenia na dystansie 192-262                11,0

Ani glebokosc, ani dystans nie sa nosnikiem. Rozni je **liczba rodzin
w portfelu** i gorny dystans. Stad `w18`: portfel jawnie roznorodny.

    python eksperymenty/E14_kompozycja/zloz_warianty.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import strategie as B  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WY = REPO / "runs" / "julian"
CEL = 100


def naturalne() -> list[str]:
    plik = REPO / "data" / "Promotory.csv"
    with open(plik, encoding="utf-8") as fh:
        wiersze = list(csv.DictReader(fh, delimiter=";"))
    return [w["sekwencja"].upper() for w in wiersze
            if len(w["sekwencja"]) == 800]


def zapisz(nazwa: str, rekordy: list[F.Rekord]) -> dict:
    raport = F.waliduj(rekordy)
    plik = WY / f"{nazwa}.fasta"
    F.zapisz(plik, raport.ok[:CEL])
    print(f"{nazwa:28s} ok={len(raport.ok):3d} odrzucone={len(raport.odrzucone)} "
          f"duplikaty={len(raport.duplikaty)}")
    return {"plik": f"{nazwa}.fasta", "n": len(raport.ok[:CEL])}


def main() -> int:
    v14 = F.czytaj(WY / "v14_glebokosc.fasta")
    v15 = F.czytaj(WY / "v15_czysta_glebokosc.fasta")
    v16 = F.czytaj(WY / "v16_mieszanka_podkrecona.fasta")
    nat = naturalne()
    print(f"podklady: v14={len(v14)} v15={len(v15)} v16={len(v16)} "
          f"naturalne={len(nat)}\n")
    meta = {}

    # --- w17: pelna kompozycja na naszym najlepszym podkladzie -------------
    # Wszystkie cztery bloki naraz. To jest "zloty strzal" wg literatury:
    # cbh1 z wymienionymi miejscami dal 5,0 x i 3,6 x.
    rek, opisy = [], []
    for i, r in enumerate(v14):
        s, opis = B.zloz(r.seq, ccaat=4, xbs="IR2", ndr=26, cre1=True, ziarno=i)
        rek.append(F.Rekord(f"K_pelna_{i:03d}_z{opis['zmian']}", s))
        opisy.append(opis)
    meta["w17_pelna_kompozycja"] = zapisz("w17_pelna_kompozycja", rek)
    z = [o["zmian"] for o in opisy]
    meta["w17_pelna_kompozycja"]["zmian_med"] = sorted(z)[len(z) // 2]
    meta["w17_pelna_kompozycja"]["cre1_rozbitych_med"] = sorted(
        o["cre1_rozbite"] for o in opisy)[len(opisy) // 2]

    # --- w18: portfel jawnie roznorodny ------------------------------------
    # Jedyna roznica miedzy v14 (14,0) a v15 (12,0) to liczba rodzin.
    # Tu jest ich piec, po 20 sztuk.
    rek = []
    rodziny = [
        ("R1_gleb", [r.seq for r in v15[:20]]),
        ("R2_pok", [r.seq for r in v14[45:65]]),
        ("R3_ccaat", [B.zloz(r.seq, ccaat=4, xbs="brak", ndr=0, cre1=False,
                             ziarno=i)[0] for i, r in enumerate(v14[:20])]),
        ("R4_xbs", [B.zloz(r.seq, ccaat=0, xbs="IR2", ndr=0, cre1=False,
                           ziarno=i)[0] for i, r in enumerate(v14[20:40])]),
        ("R5_ndr_cre1", [B.zloz(r.seq, ccaat=0, xbs="brak", ndr=26, cre1=True,
                                ziarno=i)[0] for i, r in enumerate(v16[:20])]),
    ]
    for etyk, seqs in rodziny:
        for i, s in enumerate(seqs):
            rek.append(F.Rekord(f"{etyk}_{i:03d}", s))
    meta["w18_piec_rodzin"] = zapisz("w18_piec_rodzin", rek)

    # --- w19: pivot doslownie -- naturalny podklad + pelne bloki -----------
    # Hipoteza z PIVOT.md 4. Trzy nasze pomiary jej przecza, ale zadnego
    # nie zrobiono z zainstalowanymi blokami. Dostaje wlasne zgloszenie.
    rek = []
    for i, s in enumerate(nat[:CEL]):
        z, _ = B.zloz(s, ccaat=4, xbs="IR2", ndr=26, cre1=True, ziarno=i)
        rek.append(F.Rekord(f"N_pivot_{i:03d}", z))
    meta["w19_pivot_naturalny"] = zapisz("w19_pivot_naturalny", rek)

    # --- w20: sam IR-XBS ---------------------------------------------------
    # Element o najwiekszym udokumentowanym efekcie i percentylu 0 % u dzikiego.
    # Zaden ze stu naturalnych nie ma odwroconego powtorzenia GGCTAA.
    rek = []
    for i, r in enumerate(v14):
        s, _ = B.zloz(r.seq, ccaat=0, xbs="IR2", ndr=0, cre1=False, ziarno=i)
        rek.append(F.Rekord(f"X_ir2_{i:03d}", s))
    meta["w20_tylko_xbs"] = zapisz("w20_tylko_xbs", rek)

    # --- w21: przepis cbh1 -- represor precz, aktywator na jego miejsce ----
    rek = []
    for i, r in enumerate(v14):
        s, _ = B.zloz(r.seq, ccaat=4, xbs="brak", ndr=0, cre1=True, ziarno=i)
        rek.append(F.Rekord(f"C_cbh1_{i:03d}", s))
    meta["w21_cbh1"] = zapisz("w21_cbh1", rek)

    # --- kontrola skladu ---------------------------------------------------
    print("\nelementy cis (pierwsza sekwencja kazdego pliku):")
    for nazwa in meta:
        r = F.czytaj(WY / meta[nazwa]["plik"])[0]
        print(f"  {nazwa:24s} {B.policz_elementy(r.seq)}")
    print(f"  {'v14 (podklad)':24s} {B.policz_elementy(v14[0].seq)}")

    (TU / "wyniki_warianty.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
