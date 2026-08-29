"""Operacje na sekwencjach: mutacje, statystyki, motywy.

Deterministyczne: wszystkie funkcje losowe przyjmuja `rng` albo `ziarno`,
zeby eksperymenty dalo sie odtworzyc.
"""

from __future__ import annotations

import random
from collections import Counter

ZASADY = "ACGT"
KOMPLEMENT = str.maketrans("ACGTN", "TGCAN")


def rewers_komplement(seq: str) -> str:
    return seq.translate(KOMPLEMENT)[::-1]


def gc(seq: str) -> float:
    s = seq.upper()
    n = sum(s.count(z) for z in ZASADY)
    return (s.count("G") + s.count("C")) / n if n else 0.0


def sklad(seq: str) -> dict[str, int]:
    return dict(Counter(seq.upper()))


def hamming(a: str, b: str) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def rozne_pozycje(a: str, b: str) -> list[tuple[int, str, str]]:
    """[(pozycja 1-based, zasada w a, zasada w b)]"""
    return [(i + 1, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]


def _rng(rng: random.Random | None, ziarno: int | None) -> random.Random:
    return rng if rng is not None else random.Random(ziarno)


def mutuj(
    seq: str,
    ile: int = 5,
    pozycje: list[int] | None = None,
    rng: random.Random | None = None,
    ziarno: int | None = None,
) -> str:
    """Losowe podstawienia. `pozycje` (1-based) ogranicza pule do edycji.

    `pozycje=None` -> cala sekwencja; `pozycje=[]` -> nic do zmiany.
    """
    r = _rng(rng, ziarno)
    out = list(seq)
    pula = [p - 1 for p in pozycje] if pozycje is not None else list(range(len(seq)))
    if not pula:
        return seq
    for idx in r.sample(pula, min(ile, len(pula))):
        obecna = out[idx]
        out[idx] = r.choice([z for z in ZASADY if z != obecna])
    return "".join(out)


def krzyzuj(
    a: str, b: str, punktow: int = 2, rng: random.Random | None = None, ziarno: int | None = None
) -> str:
    """Crossover wielopunktowy dwoch sekwencji tej samej dlugosci."""
    r = _rng(rng, ziarno)
    assert len(a) == len(b)
    ciecia = sorted(r.sample(range(1, len(a)), punktow))
    out, zrodlo, poprz = [], a, 0
    for c in ciecia + [len(a)]:
        out.append(zrodlo[poprz:c])
        zrodlo = b if zrodlo is a else a
        poprz = c
    return "".join(out)


def wstaw(seq: str, motyw: str, poz: int) -> str:
    """Podstawia `motyw` w miejscu `poz` (1-based), zachowujac dlugosc."""
    i = poz - 1
    if i < 0 or i + len(motyw) > len(seq):
        raise ValueError("motyw nie miesci sie w sekwencji")
    return seq[:i] + motyw.upper() + seq[i + len(motyw):]


def znajdz(seq: str, motyw: str) -> list[int]:
    """Pozycje (1-based) wystapien motywu, takze na nici komplementarnej."""
    s, m = seq.upper(), motyw.upper()
    trafienia, start = [], 0
    while (i := s.find(m, start)) != -1:
        trafienia.append(i + 1)
        start = i + 1
    return trafienia


# Kilka motywow promotorowych przydatnych przy analizie (eukarionty/grzyby).
MOTYWY = {
    "TATA": "TATAAA",
    "TATA_wariant": "TATATA",
    "CAAT": "CCAAT",
    "GC_box": "GGGCGG",
    "Inr_like": "TCAGT",
    "CreA": "SYGGRG",  # miejsce represji kataboliczej, kod IUPAC
}

IUPAC = {
    "A": "A", "C": "C", "G": "G", "T": "T",
    "R": "AG", "Y": "CT", "S": "GC", "W": "AT",
    "K": "GT", "M": "AC", "B": "CGT", "D": "AGT",
    "H": "ACT", "V": "ACG", "N": "ACGT",
}


def znajdz_iupac(seq: str, wzor: str) -> list[int]:
    """Wyszukiwanie motywu zapisanego kodem IUPAC. Pozycje 1-based."""
    s, w = seq.upper(), wzor.upper()
    trafienia = []
    for i in range(len(s) - len(w) + 1):
        if all(s[i + j] in IUPAC.get(c, c) for j, c in enumerate(w)):
            trafienia.append(i + 1)
    return trafienia


def skanuj_motywy(seq: str, motywy: dict[str, str] | None = None) -> dict[str, list[int]]:
    return {n: znajdz_iupac(seq, w) for n, w in (motywy or MOTYWY).items()}
