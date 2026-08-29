#!/usr/bin/env python3
"""E04 -- plan faktorialny 2^4: gatunek x CreA x rdzen x tlo.

Patrz PLAN.md. Czynniki dzialaja na ROZLACZNYCH zbiorach pozycji, wiec
skladaja sie w jednej sekwencji. Faza 1 nie zbudowala ani jednej kombinacji.

    python eksperymenty/E04_blok_kombinacyjny/run.py [--bez-c] [--replik N]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import (  # noqa: E402
    KATALOG, klient, kandydaci as K, metryki as M, wczytaj, zapisz,
)
from hyppe import fasta as F, seq as S  # noqa: E402

TU = Path(__file__).resolve().parent

# Rdzen Inr-podobny jako zapas, gdy E03 nie bylo uruchomione.
# Pirymidynowy trakt + Inr (YYANWYY) tuz przed TSS -- wariant literaturowy,
# swiadomie slabiej uzasadniony niz konsensus z E03.
RDZEN_ZAPASOWY = "CTCTCTCTCATCAGTCAC"   # 18 pz = okno 783-800


def rdzen_z_e03() -> tuple[str, str]:
    """(sekwencja_rdzenia, zrodlo). Preferuje konsensus ze stu naturalnych."""
    w = wczytaj(KATALOG / "E03_naturalne_promotory" / "wyniki.json")
    if w and w.get("konsensus", {}).get("rdzen", {}).get("konsensus"):
        kons = w["konsensus"]["rdzen"]["konsensus"]
        if len(kons) == M.RDZEN_DO - M.RDZEN_OD + 1:
            return kons, "konsensus 100 naturalnych promotorow (E03)"
    return RDZEN_ZAPASOWY, "wariant literaturowy Inr-podobny (E03 nieuruchomione)"


def c_wyciety() -> bool:
    """Czy E02 orzeklo ARTEFAKT -- wtedy czynnik C nie ma uzasadnienia."""
    w = wczytaj(KATALOG / "E02_artefakt_wagap" / "wyniki.json")
    if not w:
        return False
    rot = [r for r in w["rekordy"] if r["grupa"] == "rotacja"]
    if not rot:
        return False
    # szczyt zostal na koncu mimo przesuniecia tresci -> sygnal jest pozycyjny
    zostal = sum(1 for r in rot if r["metryki"]["argmax"] >= 750)
    return zostal == len(rot)


def rozbij_crea(sekw: str, poz: int = 560, ziarno: int = 0) -> str:
    """Niszczy motyw SYGGRG. Niezmienne GG na pozycjach 3-4 motywu -> GG->TT.

    Celujemy w trafienie NAJBLIZSZE `poz` (w dzikim CreA siedzi na 560), a nie
    w pierwsze w sekwencji -- edytowane warianty moga miec dodatkowe miejsca
    SYGGRG powstale przypadkiem i podmiana nie tego, co trzeba, cicho zepsulaby
    caly czynnik B planu faktorialnego.

    Replika (ziarno != 0) uzywa innego podstawienia o tym samym efekcie,
    zeby oddzielic efekt hipotezy od efektu konkretnej litery.
    """
    trafienia = S.znajdz_iupac(sekw, S.MOTYWY["CreA"])
    p = min(trafienia, key=lambda t: abs(t - poz)) if trafienia else poz
    podmiana = {0: "TT", 1: "AA", 2: "TA"}[ziarno % 3]
    return S.wstaw(sekw, podmiana, p + 2)


def zbuduj(c, dziki: str, uzyj_c: bool, replik: int) -> list[dict]:
    rdzen, zrodlo_rdzenia = rdzen_z_e03()
    print(f"czynnik C -- rdzen: {rdzen}  ({zrodlo_rdzenia})")

    # A: punkt staly kanalu gatunku (2 iteracje wg H7) -- liczony raz.
    gat = c.zastosuj_rekomendacje(c.zastosuj_rekomendacje(dziki))
    print(f"czynnik A -- wariant gatunkowy: {S.hamming(dziki, gat)} zmian od dzikiego")

    poziomy_c = (0, 1) if uzyj_c else (0,)
    out = []
    for r in range(replik):
        # D=1: tlo z dekodera, jedno wywolanie na replike (nie na komorke)
        odp = c.edycje(dziki, poziom=2, ile_kodow=8, opcji=1, ziarno=200 + r)
        tlo_dekoder = odp["opcje"][0]["sekwencja"]
        # A na tle dekodera trzeba policzyc osobno -- rekomendacje sa dla sekwencji
        gat_dekoder = c.zastosuj_rekomendacje(c.zastosuj_rekomendacje(tlo_dekoder))

        for a in (0, 1):
            for b in (0, 1):
                for cc in poziomy_c:
                    for d in (0, 1):
                        s = (gat_dekoder if a else tlo_dekoder) if d else (gat if a else dziki)
                        if b:
                            s = rozbij_crea(s, ziarno=r)
                        if cc:
                            # ZAWSZE ostatni krok: dekoder nadpisalby te edycje
                            s = K.podmien_okno(s, M.RDZEN_OD, M.RDZEN_DO, rdzen)
                        out.append({
                            "etykieta": f"E04_A{a}B{b}C{cc}D{d}_r{r:02d}",
                            "A_gatunek": a, "B_crea": b, "C_rdzen": cc, "D_tlo": d,
                            "replika": r,
                            "sekwencja": s,
                            "rodzic": tlo_dekoder if d else dziki,
                        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bez-c", action="store_true", help="wymus plan 2^3 bez rdzenia")
    ap.add_argument("--wymus-c", action="store_true",
                    help="zmierz czynnik C mimo werdyktu ARTEFAKT z E02 (patrz nizej)")
    ap.add_argument("--replik", type=int, default=3)
    args = ap.parse_args()

    c = klient()
    dziki = c.dziki_seq()

    uzyj_c = not args.bez_c
    if uzyj_c and c_wyciety():
        print("E02 orzeklo ARTEFAKT (szczyt zostal na koncu we WSZYSTKICH rotacjach)")
        if args.wymus_c:
            # E02 obalilo LOKALIZACJE szczytu, nie cala informacje w oknie 783-800:
            # `masa_rdzenia` nadal zalezy od tresci, a w E01 okazala sie najsilniejszym
            # wewnatrzpulowym korelatem werdyktu Sedziego. Wolimy ten czynnik ZMIERZYC
            # niz zalozyc, ze jest zerowy -- plan 2^3 zostaje w srodku jako polowa C=0.
            print("-> --wymus-c: czynnik C ZOSTAJE, plan 2^4 (2^3 to jego polowa C=0)")
        else:
            print("-> czynnik C wyciety, plan schodzi do 2^3")
            uzyj_c = False

    komorki = zbuduj(c, dziki, uzyj_c, args.replik)
    print(f"\n{len(komorki)} sekwencji "
          f"({2 ** (4 if uzyj_c else 3)} komorek x {args.replik} replik)\n")

    for i, k in enumerate(komorki, 1):
        m = M.metryki_mapy(c.mapa(k["sekwencja"]))
        k["metryki"] = m
        k["dystans_od_dzikiego"] = S.hamming(dziki, k["sekwencja"])
        k["bije_dzikiego"] = c.lepsza(dziki, k["sekwencja"])
        k["bije_rodzica"] = c.lepsza(k["rodzic"], k["sekwencja"])
        print(f"  [{i:2d}/{len(komorki)}] {k['etykieta']:<22} "
              f"blad_odtw={m.get('blad_odtworzenia')} "
              f"zmian_gat={m.get('zmian_pod_gatunek')} "
              f"dyst={k['dystans_od_dzikiego']:>3} "
              f"bije_dz={int(k['bije_dzikiego'])} bije_rodz={int(k['bije_rodzica'])}")

    # FASTA do wciagniecia w portfel E05
    fasta = TU / "kandydaci.fasta"
    F.zapisz(fasta, [(k["etykieta"], k["sekwencja"]) for k in komorki])

    p = zapisz(TU / "wyniki.json", {
        "eksperyment": "E04_blok_kombinacyjny",
        "dziki": dziki,
        "czynniki": ["A_gatunek", "B_crea", "C_rdzen", "D_tlo"],
        "czynnik_C_uzyty": uzyj_c,
        "rdzen_uzyty": rdzen_z_e03(),
        "replik": args.replik,
        "komorki": komorki,
    })
    print(f"\nzapisano: {p}\n         {fasta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
