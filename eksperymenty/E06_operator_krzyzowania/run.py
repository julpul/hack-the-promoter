#!/usr/bin/env python3
"""E06 -- czy krzyzowanie wygrywa jako OPERATOR, czy przez preselekcje rodzicow?

Patrz PLAN.md. Pula wgrana w fazie 1 dzieli sie na dwie czesci o dwunastokrotnie
roznym odsetku wygranych (nav 6 %, hyb 72 %), ale rodzice krzyzowek byli
zwyciezcami turnieju -- wiec efekt operatora jest pomieszany z dziedziczeniem.
Rozstrzyga ramie R2: krzyzowanie dwoch PRZEGRANYCH.

    python eksperymenty/E06_operator_krzyzowania/run.py [--na-ramie 16]
"""

from __future__ import annotations

import argparse
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import klient, metryki as M, zapisz  # noqa: E402
from hyppe import seq as S  # noqa: E402

TU = Path(__file__).resolve().parent


def zaciag_rodzicow(c, dziki: str, rund: int = 6) -> list[dict]:
    """Swiezy zaciag z /edycje + werdykt Sedziego dla kazdej sekwencji.

    Parametry jak w strategii `hybryda` (poziom 2, ile_kodow 6+runda), zeby
    ramie R3 bylo replikacja tego, co faktycznie wygralo w fazie 1, a nie
    innym eksperymentem pod ta sama nazwa.
    """
    widziane: set[str] = set()
    out: list[dict] = []
    for runda in range(1, rund + 1):
        odp = c.edycje(dziki, poziom=2, ile_kodow=6 + runda, opcji=8, ziarno=1000 + runda)
        for o in odp["opcje"]:
            s = o["sekwencja"]
            if s in widziane or s == dziki:
                continue
            widziane.add(s)
            out.append({"etykieta": f"nav_r{runda}_{o['nr']}", "sekwencja": s,
                        "bije_dzikiego": c.lepsza(dziki, s)})
    return out


def dziecko(a: str, b: str, r: random.Random) -> str:
    """Dokladnie ten sam operator, ktory zbudowal `hyb_*` w strategii hybryda."""
    return S.mutuj(S.krzyzuj(a, b, punktow=r.randint(1, 4), rng=r),
                   ile=r.randint(0, 6), rng=r)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--na-ramie", type=int, default=16)
    args = ap.parse_args()
    n = args.na_ramie

    c = klient()
    dziki = c.dziki_seq()

    print("zaciag rodzicow z /edycje ...")
    rodzice = zaciag_rodzicow(c, dziki)
    zwyc = [x for x in rodzice if x["bije_dzikiego"]]
    przeg = [x for x in rodzice if not x["bije_dzikiego"]]
    print(f"  {len(rodzice)} sekwencji, zwyciezcow {len(zwyc)}, przegranych {len(przeg)}")
    if len(zwyc) < 2:
        print("  UWAGA: mniej niz 2 zwyciezcow -- ramiona R3/R4/R5/R6 beda puste.",
              file=sys.stderr)

    r = random.Random(2026)
    ramiona: dict[str, list[dict]] = {}

    def para(zrodlo):
        a, b = r.sample(zrodlo, 2)
        return a, b

    # R1 -- surowe wyjscia dekodera (kontrola bazowa)
    ramiona["R1_dekoder_surowy"] = [
        {"etykieta": f"R1_{i:02d}", "sekwencja": x["sekwencja"],
         "rodzic_a": None, "rodzic_b": None}
        for i, x in enumerate(rodzice[:n])]

    # R2 -- RAMIE ROZSTRZYGAJACE: krzyzowka dwoch PRZEGRANYCH
    if len(przeg) >= 2:
        ramiona["R2_krzyz_przegranych"] = []
        for i in range(n):
            a, b = para(przeg)
            ramiona["R2_krzyz_przegranych"].append(
                {"etykieta": f"R2_{i:02d}", "sekwencja": dziecko(a["sekwencja"], b["sekwencja"], r),
                 "rodzic_a": a["sekwencja"], "rodzic_b": b["sekwencja"]})

    # R3 -- krzyzowka dwoch zwyciezcow (replikacja hybrydy)
    if len(zwyc) >= 2:
        ramiona["R3_krzyz_zwyciezcow"] = []
        for i in range(n):
            a, b = para(zwyc)
            ramiona["R3_krzyz_zwyciezcow"].append(
                {"etykieta": f"R3_{i:02d}", "sekwencja": dziecko(a["sekwencja"], b["sekwencja"], r),
                 "rodzic_a": a["sekwencja"], "rodzic_b": b["sekwencja"]})

    # R4 -- zwyciezca x dziki: czy drugi rodzic musi pochodzic z dekodera
    if zwyc:
        ramiona["R4_krzyz_z_dzikim"] = []
        for i in range(n):
            a = r.choice(zwyc)
            ramiona["R4_krzyz_z_dzikim"].append(
                {"etykieta": f"R4_{i:02d}", "sekwencja": dziecko(a["sekwencja"], dziki, r),
                 "rodzic_a": a["sekwencja"], "rodzic_b": dziki})

    # R5 -- KONTROLA DYSTANSU: zwyciezca + tyle samo podstawien, ile wnosi krzyzowka.
    # Liczba brana z FAKTYCZNIE zmierzonej mediany dziecko<->rodzic_a w R3,
    # zeby R5 rozniło się od R3 wylacznie zrodlem liter, nie ich liczba.
    if zwyc and ramiona.get("R3_krzyz_zwyciezcow"):
        dyst = int(st.median([S.hamming(x["sekwencja"], x["rodzic_a"])
                              for x in ramiona["R3_krzyz_zwyciezcow"]]))
        print(f"  kontrola dystansu R5: {dyst} podstawien (mediana dziecko<->rodzic w R3)")
        ramiona["R5_mutacja_o_ten_dystans"] = []
        for i in range(n):
            a = r.choice(zwyc)
            ramiona["R5_mutacja_o_ten_dystans"].append(
                {"etykieta": f"R5_{i:02d}",
                 "sekwencja": S.mutuj(a["sekwencja"], ile=dyst, rng=r),
                 "rodzic_a": a["sekwencja"], "rodzic_b": None})

    # R6 -- drugie pokolenie: krzyzowka dzieci z R3
    if len(ramiona.get("R3_krzyz_zwyciezcow", [])) >= 2:
        pokolenie1 = [x["sekwencja"] for x in ramiona["R3_krzyz_zwyciezcow"]]
        ramiona["R6_drugie_pokolenie"] = []
        for i in range(n):
            a, b = r.sample(pokolenie1, 2)
            ramiona["R6_drugie_pokolenie"].append(
                {"etykieta": f"R6_{i:02d}", "sekwencja": dziecko(a, b, r),
                 "rodzic_a": a, "rodzic_b": b})

    # ── pomiar ────────────────────────────────────────────────────────────
    rekordy = []
    for nazwa, poz in ramiona.items():
        for x in poz:
            s = x["sekwencja"]
            m = M.metryki_mapy(c.mapa(s))
            m["dystans_od_dzikiego"] = S.hamming(dziki, s)
            rek = {**x, "ramie": nazwa, "metryki": m,
                   "bije_dzikiego": c.lepsza(dziki, s)}
            for kto in ("rodzic_a", "rodzic_b"):
                p = x.get(kto)
                rek[f"bije_{kto}"] = c.lepsza(p, s) if p and p != s else None
                rek[f"dystans_{kto}"] = S.hamming(p, s) if p else None
            rekordy.append(rek)
        wyg = sum(1 for y in rekordy if y["ramie"] == nazwa and y["bije_dzikiego"])
        ile = sum(1 for y in rekordy if y["ramie"] == nazwa)
        print(f"  {nazwa:<26} bije dzikiego {wyg:>2}/{ile:<2} ({wyg / ile:5.0%})")

    print("\n=== PODSUMOWANIE RAMION ===")
    print(f"{'ramie':<26}{'n':>4}{'bije dzikiego':>16}{'bije rodzica_a':>17}"
          f"{'dyst. do rodzica':>18}")
    for nazwa in ramiona:
        g = [x for x in rekordy if x["ramie"] == nazwa]
        wyg = sum(x["bije_dzikiego"] for x in g)
        br = [x["bije_rodzic_a"] for x in g if x["bije_rodzic_a"] is not None]
        dy = [x["dystans_rodzic_a"] for x in g if x["dystans_rodzic_a"] is not None]
        print(f"{nazwa:<26}{len(g):>4}{f'{wyg}/{len(g)} ({wyg / len(g):.0%})':>16}"
              f"{(f'{sum(br)}/{len(br)}' if br else '-'):>17}"
              f"{(f'{st.median(dy):.0f}' if dy else '-'):>18}")

    p = zapisz(TU / "wyniki.json", {
        "eksperyment": "E06_operator_krzyzowania",
        "dziki": dziki,
        "na_ramie": n,
        "rodzice_zaciag": rodzice,
        "rekordy": rekordy,
    })
    print(f"\nzapisano: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
