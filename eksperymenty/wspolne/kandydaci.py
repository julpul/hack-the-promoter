"""Budowanie sekwencji kontrolnych i wczytywanie zbiorow referencyjnych.

Sercem jest zestaw przeksztalcen rozdzielajacych **tresc** od **pozycji**.
Kazde z nich zachowuje dlugosc 800 pz i alfabet ACGT, wiec wynik nadaje sie
zarowno do /nawigator/mapa, jak i do zgloszenia.

    przetasuj  - ten sam sklad zasad, zniszczona kolejnosc     (kontrola tresci)
    obroc      - ta sama tresc lokalna, przesunieta pozycja    (kontrola pozycji)
    odwroc     - ta sama tresc, odwrocona kolejnosc            (kontrola pozycji)
    losowa     - dopasowany GC, zadnej tresci                  (kontrola zerowa)

Rozstrzygajaca jest **rotacja**: zachowuje kazdy lokalny motyw i tylko
przesuwa go wzgledem krawedzi wejscia. Jesli sygnal modelu idzie za trescia,
szczyt przesunie sie razem z nia; jesli siedzi na krawedzi, zostanie w miejscu.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from .io import REPO

ZASADY = "ACGT"
GC_DZIKIEGO = 0.475
DLUGOSC = 800


def przetasuj(seq: str, ziarno: int = 0) -> str:
    """Permutacja zasad. Zachowuje sklad, niszczy wszystkie motywy i pozycje."""
    r = random.Random(ziarno)
    litery = list(seq)
    r.shuffle(litery)
    return "".join(litery)


def obroc(seq: str, o: int) -> str:
    """Rotacja cykliczna o `o` pozycji w lewo.

    Zachowuje CALA tresc lokalna (poza jednym szwem) i tylko przesuwa ja
    wzgledem krawedzi. To jest kluczowa kontrola eksperymentu E02.
    Pozycja p w oryginale ladauje na pozycji ((p - 1 - o) mod 800) + 1.
    """
    o %= len(seq)
    return seq[o:] + seq[:o]


def gdzie_po_rotacji(poz: int, o: int, dlugosc: int = DLUGOSC) -> int:
    """Gdzie (1-based) ladauje pozycja `poz` po `obroc(seq, o)`."""
    return ((poz - 1 - o) % dlugosc) + 1


def odwroc(seq: str) -> str:
    """Odwrocenie kolejnosci (NIE rewers-komplement -- chcemy czystego testu
    pozycji, bez zmiany skladu i bez zmiany nici)."""
    return seq[::-1]


def losowa(dlugosc: int = DLUGOSC, gc: float = GC_DZIKIEGO, ziarno: int = 0) -> str:
    """Sekwencja losowa o zadanym GC. Kontrola zerowa: brak jakiejkolwiek tresci."""
    r = random.Random(ziarno)
    out = []
    for _ in range(dlugosc):
        out.append(r.choice("GC") if r.random() < gc else r.choice("AT"))
    return "".join(out)


def podmien_okno(seq: str, od: int, do: int, wypelniacz: str | None = None,
                 ziarno: int = 0) -> str:
    """Podmienia okno [od, do] (1-based, wlacznie) na `wypelniacz` albo losowo.

    Uzywane do dwoch rzeczy: niszczenia rdzenia (kontrola w E02) i wstawiania
    zaprojektowanego rdzenia po dekodowaniu (czynnik C w E04).
    """
    dlug = do - od + 1
    if wypelniacz is None:
        r = random.Random(ziarno)
        wypelniacz = "".join(r.choice(ZASADY) for _ in range(dlug))
    if len(wypelniacz) != dlug:
        raise ValueError(f"wypelniacz ma {len(wypelniacz)} pz, okno ma {dlug}")
    return seq[: od - 1] + wypelniacz.upper() + seq[do:]


def do_800(seq: str, kotwica: str = "3prim") -> str:
    """Przycina lub dopelnia sekwencje do 800 pz.

    `kotwica='3prim'` zachowuje koniec 3' -- promotory sa wyrownane do miejsca
    startu transkrypcji, wiec to koniec sekwencji jest punktem odniesienia
    i to jego nie wolno ruszyc. Dopelniamy 'N' (dozwolone do 10 %).
    """
    s = "".join(c for c in seq.upper() if c in "ACGTN")
    if len(s) >= DLUGOSC:
        return s[-DLUGOSC:] if kotwica == "3prim" else s[:DLUGOSC]
    brak = DLUGOSC - len(s)
    return ("N" * brak) + s if kotwica == "3prim" else s + ("N" * brak)


def wczytaj_naturalne(sciezka: Path | str | None = None) -> list[dict]:
    """Wczytuje data/promotory_100.csv (separator ';').

    Zwraca [{'nazwa':..., 'sekwencja':..., 'dlugosc_oryginalna':..., ...}].
    Sekwencje sa doprowadzone do 800 pz z kotwica na koncu 3'.
    Kolumny CSV bywaja rozne miedzy wydaniami materialow, wiec nazwa jest
    wyszukiwana elastycznie.
    """
    if sciezka:
        p = Path(sciezka)
    else:
        # nazwa pliku bywa rozna miedzy wydaniami materialow
        kandydaci_nazw = ["promotory_100.csv", "Promotory.csv", "promotory.csv",
                          "Promotory_100.csv"]
        p = next((REPO / "data" / n for n in kandydaci_nazw
                  if (REPO / "data" / n).exists()),
                 REPO / "data" / "promotory_100.csv")
    if not p.exists():
        raise FileNotFoundError(
            f"brak {p}. To plik z materialow hackathonu -- wrzuc go do data/ "
            "(patrz data/README.md)."
        )
    with open(p, encoding="utf-8") as fh:
        proba = fh.read(4096)
        fh.seek(0)
        sep = ";" if proba.count(";") >= proba.count(",") else ","
        wiersze = list(csv.DictReader(fh, delimiter=sep))

    out = []
    for i, w in enumerate(wiersze):
        klucze = {k.lower().strip(): k for k in w if k}
        k_seq = next((klucze[k] for k in klucze
                      if k in ("sekwencja", "sequence", "seq", "promotor")), None)
        if k_seq is None:  # ostatnia deska ratunku: najdluzsza wartosc w wierszu
            k_seq = max(w, key=lambda k: len(w.get(k) or ""))
        k_naz = next((klucze[k] for k in klucze
                      if k in ("nazwa", "name", "id", "gatunek", "gen")), None)
        surowa = (w.get(k_seq) or "").strip()
        if not surowa:
            continue
        out.append({
            "nazwa": (w.get(k_naz) or f"nat_{i:03d}").strip(),
            "sekwencja": do_800(surowa),
            "dlugosc_oryginalna": len(surowa),
            "surowe_pola": {k: v for k, v in w.items() if k and k != k_seq},
        })
    return out


def wczytaj_pule(sciezka: Path | str | None = None, ile: int | None = None) -> dict[str, str]:
    """Wczytuje istniejaca pule FASTA (domyslnie runs/julian/pula.fasta)."""
    from hyppe import fasta as F

    p = Path(sciezka) if sciezka else REPO / "runs" / "julian" / "pula.fasta"
    if not p.exists():
        return {}
    pary = [(r.nazwa, r.seq) for r in F.czytaj(p)]
    return dict(pary[:ile] if ile else pary)
