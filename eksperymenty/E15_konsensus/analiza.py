#!/usr/bin/env python3
"""E15 -- analiza konsensusu v14_glebokosc. Faza offline, 0 wywolan API.

Pytanie: co dostaniemy, uzgadniajac 100 sekwencji v14 kolumna po kolumnie?

Uklad danych pozwala odpowiedziec zanim wydamy jedno wywolanie. Wszystkie
100 sekwencji ma dokladnie 800 pz, sam alfabet ACGT, zero przerw -- dekoder
robi wylacznie **podstawienia**. Uliniowienie jest wiec kolumnowe i
jednoznaczne, bez algorytmu i bez kar za przerwy.

To samo jednak znaczy, ze konsensus liczymy po probie, ktora wg W21 sklada
sie z **65 osobnych skupien** (zadna para nie jest ta sama rodzina). Glosowanie
wiekszosciowe po niezaleznych losowaniach, z ktorych kazde zmienia ~13-21 %
pozycji w INNYCH miejscach, musi zwracac zasade dzikiego wszedzie tam, gdzie
dekoder nie ma systematycznej preferencji.

Ten skrypt sprawdza, czy tak jest, i rozdziela dwie rzeczy, ktore konsensus
miesza:

  * skladowa LOSOWA dekodera  -> kolumny, gdzie wygrywa dziki,
  * skladowa SYSTEMATYCZNA    -> kolumny, gdzie wiekszosc odchodzi od dzikiego.

Druga jest interesujaca: to jest podpis dekodera, ktorego nigdy nie wyodrebnilismy.

    python eksperymenty/E15_konsensus/analiza.py
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"
ZASADY = "ACGT"

# Motywy wg W27 / PIVOT.md 3.4. Skanujemy obie nici tam, gdzie motyw
# nie jest palindromiczny -- CCAAT czytamy tez jako ATTGG.
MOTYWY = {
    "CCAAT": ["CCAAT", "ATTGG"],
    "GGCTAA (XBS rdzen)": ["GGCTAA", "TTAGCC"],
    "GGCWWW (XBS szeroki)": ["GGCWWW", "WWWGCC"],
    "SYGGRG (CreA/Cre1)": ["SYGGRG", "CYCCRS"],
    "TATAAA": ["TATAAA", "TTTATA"],
}


def wczytaj_dzikiego() -> str:
    rek = F.czytaj(REPO / "data" / "dziki.fasta")
    return rek[0].seq.upper()


def blok(nazwa: str) -> str:
    """A = glebokosc, B = pokolenia, D = dopelnienie, K = kontrola."""
    return nazwa.split("_")[0]


def kolumny(seqs: list[str]) -> list[Counter]:
    return [Counter(s[i] for s in seqs) for i in range(len(seqs[0]))]


def konsensus(kol: list[Counter]) -> str:
    # Remisy rozstrzygamy alfabetycznie -- deterministycznie i odnotowane.
    return "".join(sorted(k.items(), key=lambda t: (-t[1], t[0]))[0][0] for k in kol)


def ic_kolumny(k: Counter) -> float:
    """Informacja pozycyjna w bitach: 2 - H. Maks 2 przy pelnej konserwacji."""
    n = sum(k.values())
    h = -sum((c / n) * math.log2(c / n) for c in k.values() if c)
    return 2.0 - h


def traktyat(seq: str, minimum: int = 8) -> list[tuple[int, int]]:
    """[(poczatek 1-based, dlugosc)] ciagow zlozonych wylacznie z A/T."""
    out, start = [], None
    for i, z in enumerate(seq):
        if z in "AT":
            start = i if start is None else start
        else:
            if start is not None and i - start >= minimum:
                out.append((start + 1, i - start))
            start = None
    if start is not None and len(seq) - start >= minimum:
        out.append((start + 1, len(seq) - start))
    return out


def skan(seq: str) -> dict[str, list[int]]:
    return {n: sorted(p for w in wzory for p in S.znajdz_iupac(seq, w))
            for n, wzory in MOTYWY.items()}


def main() -> int:
    dziki = wczytaj_dzikiego()
    rek = F.czytaj(WYJSCIE / "v14_glebokosc.fasta")
    seqs = [r.seq.upper() for r in rek]
    n = len(seqs)

    print("=" * 72)
    print("1. ULINIOWIENIE")
    print("=" * 72)
    print(f"sekwencji            : {n}")
    print(f"dlugosci             : {set(len(s) for s in seqs)} -- wszystkie rowne")
    print(f"alfabet              : {sorted(set(''.join(seqs)))}")
    print("przerwy (indele)     : brak -- dekoder robi tylko podstawienia")
    print("=> uliniowienie kolumnowe, bez algorytmu MSA i bez kar za przerwy")

    bloki = Counter(blok(r.nazwa) for r in rek)
    print(f"\nsklad pliku          : {dict(bloki)}")
    print("   A = glebokosc (blad_odtworzenia 9-19) | B = 2./3. pokolenie")
    print("   D = dopelnienie z tego samego przesiewu | K = kontrola z v4")

    d_od_dzikiego = [S.hamming(dziki, s) for s in seqs]
    print(f"\ndystans od dzikiego  : {min(d_od_dzikiego)} - "
          f"{sorted(d_od_dzikiego)[n // 2]} - {max(d_od_dzikiego)} pz")

    # --- parami: czy to jedna rodzina, czy niezalezne losowania ---
    import itertools
    pary = [S.hamming(a, b) for a, b in itertools.combinations(seqs, 2)]
    print(f"dystans miedzy para  : {min(pary)} - {sorted(pary)[len(pary) // 2]}"
          f" - {max(pary)} pz  (n = {len(pary)} par)")
    print(f"   par blizej niz 40 pz: {sum(1 for p in pary if p < 40)}"
          "   <- W21: kazde ziarno to osobne skupienie")

    print()
    print("=" * 72)
    print("2. KONSENSUS")
    print("=" * 72)
    kol = kolumny(seqs)
    kon = konsensus(kol)

    zgodne_z_dzikim = sum(1 for i, z in enumerate(kon) if z == dziki[i])
    print(f"konsensus vs dziki   : {800 - zgodne_z_dzikim} roznic na 800")
    print(f"   zgodnosc          : {100 * zgodne_z_dzikim / 800:.1f} %")
    print(f"konsensus vs ziarna  : {min(S.hamming(kon, s) for s in seqs)} - "
          f"{sorted(S.hamming(kon, s) for s in seqs)[n // 2]} - "
          f"{max(S.hamming(kon, s) for s in seqs)} pz")

    # rozklad czestosci zasady wiekszosciowej
    czest = [max(k.values()) / n for k in kol]
    prog = Counter()
    for c in czest:
        if c >= 0.95:
            prog[">=95%"] += 1
        elif c >= 0.80:
            prog["80-95%"] += 1
        elif c >= 0.60:
            prog["60-80%"] += 1
        else:
            prog["<60%"] += 1
    print(f"\nczestosc zasady wiekszosciowej w kolumnie:")
    for k in (">=95%", "80-95%", "60-80%", "<60%"):
        print(f"   {k:>7} : {prog[k]:>3} kolumn")

    ic = [ic_kolumny(k) for k in kol]
    print(f"\ninformacja pozycyjna : {min(ic):.3f} - "
          f"{sorted(ic)[400]:.3f} - {max(ic):.3f} bit")

    # --- podpis dekodera: kolumny, gdzie wiekszosc ODCHODZI od dzikiego ---
    print()
    print("=" * 72)
    print("3. PODPIS DEKODERA -- gdzie wiekszosc odchodzi od dzikiego")
    print("=" * 72)
    podpis = []
    for i, k in enumerate(kol):
        udzial_dzikiego = k.get(dziki[i], 0) / n
        zwyciezca, ile = sorted(k.items(), key=lambda t: (-t[1], t[0]))[0]
        if zwyciezca != dziki[i]:
            podpis.append({"poz": i + 1, "dziki": dziki[i], "konsensus": zwyciezca,
                           "czestosc": round(ile / n, 3),
                           "udzial_dzikiego": round(udzial_dzikiego, 3)})
    podpis.sort(key=lambda x: -x["czestosc"])
    print(f"kolumn, gdzie konsensus != dziki : {len(podpis)}")
    if podpis:
        print(f"\n{'poz':>5} {'dziki':>5} {'kons':>5} {'czest':>7} {'dziki%':>7}")
        for w in podpis[:25]:
            print(f"{w['poz']:>5} {w['dziki']:>5} {w['konsensus']:>5}"
                  f" {w['czestosc']:>7.2f} {w['udzial_dzikiego']:>7.2f}")
        if len(podpis) > 25:
            print(f"   ... i {len(podpis) - 25} wiecej")

    # ile kolumn ma dzikiego ponizej 50% -- czyli dekoder go realnie wypiera
    wyparte = [i + 1 for i, k in enumerate(kol) if k.get(dziki[i], 0) / n < 0.5]
    print(f"\nkolumn z udzialem dzikiego < 50 % : {len(wyparte)}")

    print()
    print("=" * 72)
    print("4. MOTYWY -- dziki vs konsensus vs ziarna")
    print("=" * 72)
    m_dziki, m_kon = skan(dziki), skan(kon)
    m_ziarna = [skan(s) for s in seqs]
    print(f"{'motyw':<24} {'dziki':>6} {'kons':>6} {'ziarna: min-med-max':>22}"
          f" {'% z >=1':>8}")
    for nazwa in MOTYWY:
        licz = sorted(len(m[nazwa]) for m in m_ziarna)
        maja = sum(1 for m in m_ziarna if m[nazwa])
        print(f"{nazwa:<24} {len(m_dziki[nazwa]):>6} {len(m_kon[nazwa]):>6}"
              f" {licz[0]:>8} {licz[n // 2]:>6} {licz[-1]:>6}"
              f" {100 * maja / n:>7.0f}%")

    t_dziki, t_kon = traktyat(dziki), traktyat(kon)
    t_ziarna = sorted(len(traktyat(s)) for s in seqs)
    print(f"{'trakt A/T >= 8 pz':<24} {len(t_dziki):>6} {len(t_kon):>6}"
          f" {t_ziarna[0]:>8} {t_ziarna[n // 2]:>6} {t_ziarna[-1]:>6}")

    print(f"\npozycje CCAAT w konsensusie : {m_kon['CCAAT'] or '-- brak --'}")
    print(f"pozycje CCAAT w dzikim      : {m_dziki['CCAAT'] or '-- brak --'}")

    gc_ziarna = sorted(S.gc(s) for s in seqs)
    print(f"\nGC: dziki {S.gc(dziki):.3f} | konsensus {S.gc(kon):.3f} |"
          f" ziarna {gc_ziarna[0]:.3f} - {gc_ziarna[n // 2]:.3f} - {gc_ziarna[-1]:.3f}")

    # --- konsensusy blokowe: czy blok A (glebokosc) ma inny podpis niz B ---
    print()
    print("=" * 72)
    print("5. KONSENSUS PER BLOK -- czy glebokosc i pokolenia zbiegaja tam samo")
    print("=" * 72)
    per_blok = {}
    for b in ("A", "B", "D", "K"):
        grupa = [r.seq.upper() for r in rek if blok(r.nazwa) == b]
        if len(grupa) < 5:
            continue
        kb = konsensus(kolumny(grupa))
        per_blok[b] = kb
        print(f"blok {b} (n={len(grupa):>3}) : vs dziki {S.hamming(dziki, kb):>3} pz"
              f" | vs konsensus globalny {S.hamming(kon, kb):>3} pz"
              f" | CCAAT {len(skan(kb)['CCAAT'])}")

    (TU / "konsensus.json").write_text(json.dumps({
        "n": n, "dlugosc": 800,
        "konsensus": kon,
        "dystans_konsensus_dziki": 800 - zgodne_z_dzikim,
        "podpis_dekodera": podpis,
        "kolumny_dziki_ponizej_50pct": wyparte,
        "motywy_konsensus": {k: v for k, v in m_kon.items()},
        "motywy_dziki": {k: v for k, v in m_dziki.items()},
        "konsensus_per_blok": {b: s for b, s in per_blok.items()},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nzapisano -> {TU / 'konsensus.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
