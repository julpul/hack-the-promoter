#!/usr/bin/env python3
"""E09 -- trzy taktyki na trzech rozlacznych osiach, kazda osobnym plikiem.

Po W24 (rozklad ziaren dekodera ma sufit) potrzebny jest INNY rozklad, a nie
wieksza proba z tego samego. Trzy niezalezne zaklady:

  K1b  ziarna z v4 + edycje gatunkowe   -> os, ktorej Sedzia nie widzi
  K5   naturalnosc (blad_odtworzenia 63-95) -> inny rozklad wprost
  K4   test prawa Goodharta             -> pomiar rozjazdu proxy

    python eksperymenty/E09_trzy_taktyki/run.py [--taktyka K1b|K5|K4|wszystkie]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402
from eksperymenty.wspolne import kandydaci as K  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"
CEL = 100

# Motywy rdzeniowe uzywane w K4. TATAAA to kanoniczny TATA-box, CCAAT i GGGCGG
# to klasyczne elementy proksymalne. Upychamy je celowo ponad miare.
MOTYWY_K4 = ["TATAAA", "TATAAA", "CCAAT", "GGGCGG", "TATAAA", "CCAAT"]


# ─────────────────────────── K1b ───────────────────────────

def zbuduj_k1b(c: Client) -> list[F.Rekord]:
    """100 ziaren z v4, kazde z naniesionymi rekomendacjami gatunkowymi."""
    zrodlo = WYJSCIE / "v4.fasta"
    if not zrodlo.exists():
        raise SystemExit(f"brak {zrodlo} -- najpierw zloz portfel v4")
    ziarna = F.czytaj(zrodlo)
    out, bez_zmian, suma_zmian = [], 0, 0
    for i, r in enumerate(ziarna, 1):
        m = c.mapa(r.seq, od=0, ile=800)
        po = c.zastosuj_rekomendacje(r.seq, m)
        d = S.hamming(r.seq, po)
        suma_zmian += d
        if d == 0:
            bez_zmian += 1
        out.append(F.Rekord(f"K1b_{i:03d}_gat{d}", po))
        if i % 25 == 0:
            print(f"    {i}/{len(ziarna)} (srednio {suma_zmian/i:.1f} zmian gatunkowych)")
    print(f"  ziaren bez zadnej rekomendacji: {bez_zmian}/{len(ziarna)}")
    print(f"  srednio zmian gatunkowych na sekwencje: {suma_zmian/len(ziarna):.2f}")
    return out


# ─────────────────────────── K5 ───────────────────────────

def zbuduj_k5(c: Client, dziki: str) -> list[F.Rekord]:
    """Chimery dziki x naturalny promotor -- prawdziwe DNA po obu stronach.

    Cel: `blad_odtworzenia` w zakresie naturalnym (63-95), a nie ~21 jak
    wyjscia dekodera (W13). To jedyny sposob na INNY rozklad po W24.
    """
    nat = K.wczytaj_naturalne()
    r = random.Random(2026)
    out = []
    # ciecia rozlozone po calej dlugosci; wiecej ciec blisko konca, bo tam
    # promotor jest wyrownany do TSS i tam siedzi rdzen
    ciecia = [80, 160, 240, 320, 400, 480, 560, 620, 680, 720, 760, 780]
    for i, n in enumerate(nat[:CEL]):
        ciecie = ciecia[i % len(ciecia)]
        if i % 2 == 0:
            s = dziki[:ciecie] + n["sekwencja"][ciecie:]   # koniec od naturalnego
            opis = f"n{ciecie}"
        else:
            s = n["sekwencja"][:ciecie] + dziki[ciecie:]   # koniec od dzikiego
            opis = f"d{ciecie}"
        out.append(F.Rekord(f"K5_{i:03d}_{opis}_{n['nazwa'][:12]}", s))
    # kontrola: kilka czystych naturalnych i dziki z drobnymi recznymi zmianami
    for j in range(4):
        out[j] = F.Rekord(f"K5_{j:03d}_czysty_{nat[j]['nazwa'][:12]}",
                          nat[j]["sekwencja"])
    for j in range(4, 8):
        out[j] = F.Rekord(f"K5_{j:03d}_dzikiRecznie",
                          S.mutuj(dziki, ile=10 * (j - 3), ziarno=j))
    return out


# ─────────────────────────── K4 ───────────────────────────

def zbuduj_k4(dziki: str) -> list[F.Rekord]:
    """Sekwencje celowo przesadzone pod Sedziego: upchane motywy promotorowe.

    Jesli Sedzia je pokocha, a ranking nie drgnie -- mamy udokumentowany
    rozjazd proxy (prawo Goodharta), czyli wynik metodyczny niezalezny od miejsca.
    """
    r = random.Random(7)
    out = []
    for i in range(CEL):
        ile_motywow = 2 + (i % 14)          # od 2 do 15 wstawek
        s = dziki
        pozycje = sorted(r.sample(range(20, 780), ile_motywow))
        # odsuwamy kolizje, zeby wstawki sie nie nadpisywaly
        wybrane = []
        for p in pozycje:
            if not wybrane or p - wybrane[-1] >= 8:
                wybrane.append(p)
        for j, p in enumerate(wybrane):
            s = S.wstaw(s, MOTYWY_K4[j % len(MOTYWY_K4)], p)
        out.append(F.Rekord(f"K4_{i:03d}_m{len(wybrane)}", s))
    return out


# ─────────────────────────── wspolne ───────────────────────────

def zapisz_i_zmierz(c: Client, dziki: str, rekordy: list[F.Rekord],
                    nazwa_pliku: str, probka: int = 20) -> dict:
    raport = F.waliduj(rekordy)
    sciezka = WYJSCIE / nazwa_pliku
    F.zapisz(sciezka, raport.ok[:CEL])
    print("  " + raport.podsumowanie().replace("\n", "\n  "))

    r = random.Random(0)
    prob = r.sample(raport.ok[:CEL], min(probka, len(raport.ok)))
    bramka = sum(1 for x in prob if c.lepsza(dziki, x.seq))
    bledy = []
    for x in prob[:8]:
        bledy.append(c.mapa(x.seq, od=0, ile=800)["blad_odtworzenia"])
    print(f"  bramka Sedziego: {bramka}/{len(prob)}")
    print(f"  blad_odtworzenia (8 sztuk): {sorted(bledy)}")
    print(f"  zapisano -> {sciezka}")
    return {"plik": str(sciezka.relative_to(REPO)), "n": len(raport.ok[:CEL]),
            "bramka": f"{bramka}/{len(prob)}", "blad_odtworzenia": sorted(bledy)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--taktyka", default="wszystkie",
                    choices=["K1b", "K5", "K4", "wszystkie"])
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    wyniki = {}

    if a.taktyka in ("K1b", "wszystkie"):
        print("\n=== K1b: ziarna v4 + edycje gatunkowe ===")
        wyniki["K1b"] = zapisz_i_zmierz(
            c, dziki, zbuduj_k1b(c), "v5_K1b_gatunkowa.fasta")

    if a.taktyka in ("K5", "wszystkie"):
        print("\n=== K5: naturalnosc (chimery z prawdziwym DNA) ===")
        wyniki["K5"] = zapisz_i_zmierz(
            c, dziki, zbuduj_k5(c, dziki), "v6_K5_naturalnosc.fasta")

    if a.taktyka in ("K4", "wszystkie"):
        print("\n=== K4: test prawa Goodharta (upchane motywy) ===")
        wyniki["K4"] = zapisz_i_zmierz(
            c, dziki, zbuduj_k4(dziki), "v7_K4_goodhart.fasta")

    (TU / "wyniki.json").write_text(
        json.dumps({"eksperyment": "E09_trzy_taktyki", "taktyki": wyniki},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nzapisano {TU / 'wyniki.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
