#!/usr/bin/env python3
"""E14 -- bloki cis jako skladalne funkcje, niezalezne od podkladu.

`PIVOT.md` proponowal bloki (CCAAT, XBS, poli(dA:dT), rozbicie Cre1)
instalowane na **naturalnym** promotorze. Podklad z pivota upadl -- trzy
pomiary mowia, ze naturalne DNA szkodzi (`v6` nie pobil, `v11` = 4,0 przy
linii bazowej 5,0), a v14 wygral idac w **przeciwna** strone rozkladu
(`blad_odtworzenia` 9-19 zamiast naturalnych 63-95). Szczegoly:
`eksperymenty/E14_kompozycja/PLAN.md` sekcja 0.1.

Zostaje biologia. Kazda funkcja tutaj przyjmuje dowolna sekwencje 800 pz
i zwraca sekwencje 800 pz -- podklad jest parametrem, nie zalozeniem.
Dzieki temu ten sam kod obsluzy ziarno dekodera, dzikiego i promotor
naturalny, a roznica miedzy nimi staje sie mierzalna zamiast wbudowana.

Uklad wspolrzednych: TSS = koniec sekwencji. Pozycja -1 to ostatnia zasada,
wiec indeks 1-based liczymy jako `800 + d`. Rdzen -50..0 (indeksy 751-800)
jest nietykalny -- log-odds dzikiego wobec PWM ze stu naturalnych to 3,67
przy medianie 2,97 (percentyl 52 %), nie ma tam czego naprawiac.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import seq as S  # noqa: E402

DLUGOSC = 800
RDZEN_OD = -50          # ponizej tej pozycji nie ruszamy niczego

# --- motywy z literatury -----------------------------------------------------
# cbh1 T. reesei: wymiana osmiu miejsc represora ACE1 na miejsca aktywatorow
# (ACE2, Hap2/3/5, Xyr1) dala 5,0 x i 3,6 x wiecej wydzielanej mannanazy.
CCAAT = "CCAAT"                       # Hap2/3/5 (CBC), aktywator ogolny
XBS_RDZEN = "GGCTAA"                  # rdzen miejsca Xyr1/ACE2
# xyn1: wyfootprintowany odwrocony powtorzony XBS, dwa GGCTAA rozdzielone 10 pz
XBS_IR = "GGCTAAATGCGACATCTTAGCC"
CRE1 = "SYGGRG"                       # miejsce represji katabolicznej (IUPAC)


def _idx(d: int) -> int:
    """Pozycja 1-based z odleglosci od TSS (d < 0)."""
    return DLUGOSC + d


def _wolne(d: int, dlugosc: int) -> bool:
    """Czy blok [d, d+dlugosc) miesci sie i nie wchodzi w rdzen."""
    return d + dlugosc <= RDZEN_OD and _idx(d) >= 1


def wstaw_ccaat(seq: str, ile: int = 4,
                pozycje: tuple[int, ...] = (-290, -250, -210, -170)) -> str:
    """Instaluje `ile` miejsc CCAAT na wskazanych odlegloscich od TSS.

    Dziki `pks1` ma ich zero przy medianie 2 u stu naturalnych i 81 % rodzaju
    z co najmniej jednym -- percentyl 0 %.
    """
    for d in pozycje[:ile]:
        if _wolne(d, len(CCAAT)):
            seq = S.wstaw(seq, CCAAT, _idx(d))
    return seq


def wstaw_xbs(seq: str, tryb: str = "IR2", start: int = -450) -> str:
    """Miejsca Xyr1. `tryb`: 'brak' | 'tandem4' | 'IR1' | 'IR2'.

    Praca o ukladzie elementow cis w T. reesei: konfiguracja wazy wiecej niz
    liczba kopii, a odwrocony powtorzony uklad XBS silnie podnosi aktywnosc
    `cbh1`. Zaden ze stu naturalnych promotorow nie ma odwroconego powtorzenia
    GGCTAA -- to jest element inzynierski, nie skopiowany z natury.
    """
    if tryb == "brak":
        return seq
    if tryb == "tandem4":
        for i in range(4):
            d = start + i * 12
            if _wolne(d, len(XBS_RDZEN)):
                seq = S.wstaw(seq, XBS_RDZEN, _idx(d))
        return seq
    powtorzen = 2 if tryb == "IR2" else 1
    for i in range(powtorzen):
        d = start + i * 60
        if _wolne(d, len(XBS_IR)):
            seq = S.wstaw(seq, XBS_IR, _idx(d))
    return seq


def wstaw_ndr(seq: str, dlugosc: int = 26, start: int = -130,
              ziarno: int = 0) -> str:
    """Trakt poli(dA:dT) -- region wolny od nukleosomu powyzej rdzenia.

    Manipulacja traktami w `AOX1` u Pichia pastoris dala biblioteke
    o aktywnosci 0,25-3,5 x dzikiego. Dziki ma 3 trakty >= 8 pz przy
    medianie 5 u naturalnych.
    """
    if dlugosc <= 0 or not _wolne(start, dlugosc):
        return seq
    r = random.Random(ziarno)
    # Czysty poli-A bywa odrzucany jako niskozlozony; robimy trakt A/T
    # z przewaga A, co zachowuje sztywnosc helisy i sygnal NDR.
    trakt = "".join("A" if r.random() < 0.8 else "T" for _ in range(dlugosc))
    return S.wstaw(seq, trakt, _idx(start))


def rozbij_cre1(seq: str, ziarno: int = 0) -> tuple[str, int]:
    """Psuje wszystkie miejsca SYGGRG jednym podstawieniem kazde.

    Zwraca (sekwencja, ile_rozbito). Rdzen -50..0 zostaje nietkniety.
    Wymiana miejsc represora to rdzen metody z `cbh1`; my na razie tylko
    represor znosimy, bo aktywatory dokladamy osobnymi blokami.
    """
    r = random.Random(ziarno)
    rozbite = 0
    for _ in range(20):                       # motywy moga sie nakladac
        trafienia = [p for p in S.znajdz_iupac(seq, CRE1)
                     if p + len(CRE1) - 1 <= _idx(RDZEN_OD)]
        if not trafienia:
            break
        p = trafienia[0]
        i = p + 2                             # srodkowe G w SYGGRG
        obecna = seq[i - 1]
        seq = seq[:i - 1] + r.choice([z for z in "ACGT" if z != obecna]) + seq[i:]
        rozbite += 1
    return seq, rozbite


def zloz(seq: str, ccaat: int = 4, xbs: str = "IR2", ndr: int = 26,
         cre1: bool = True, ziarno: int = 0) -> tuple[str, dict]:
    """Sklada pelny wariant. Zwraca (sekwencja, opis_zmian).

    Kazdy przelacznik da sie wylaczyc, wiec ten sam kod obsluguje plan
    czynnikowy i atrybucje przez ranking.
    """
    start, rozbite = seq, 0
    if cre1:
        seq, rozbite = rozbij_cre1(seq, ziarno=ziarno)
    if ndr:
        seq = wstaw_ndr(seq, dlugosc=ndr, ziarno=ziarno)
    if ccaat:
        seq = wstaw_ccaat(seq, ile=ccaat)
    if xbs != "brak":
        seq = wstaw_xbs(seq, tryb=xbs)
    assert len(seq) == DLUGOSC, f"dlugosc {len(seq)} != {DLUGOSC}"
    assert seq[_idx(RDZEN_OD):] == start[_idx(RDZEN_OD):], "ruszony rdzen"
    return seq, {
        "ccaat": ccaat, "xbs": xbs, "ndr": ndr,
        "cre1_rozbite": rozbite,
        "zmian": S.hamming(start, seq),
    }


def policz_elementy(seq: str) -> dict[str, int]:
    """Skan obu nici -- do porownania podkladu przed i po zlozeniu."""
    rc = S.rewers_komplement(seq)
    return {
        "CCAAT": len(S.znajdz(seq, CCAAT)) + len(S.znajdz(rc, CCAAT)),
        "GGCTAA": len(S.znajdz(seq, XBS_RDZEN)) + len(S.znajdz(rc, XBS_RDZEN)),
        "Cre1": len(S.znajdz_iupac(seq, CRE1)) + len(S.znajdz_iupac(rc, CRE1)),
        "trakty_AT8": len([p for p in range(len(seq) - 7)
                           if set(seq[p:p + 8]) <= {"A", "T"}]),
    }


if __name__ == "__main__":
    # Samokontrola bez sieci: bloki musza zachowac dlugosc i rdzen.
    r = random.Random(1)
    proba = "".join(r.choice("ACGT") for _ in range(DLUGOSC))
    przed = policz_elementy(proba)
    zlozona, opis = zloz(proba)
    po = policz_elementy(zlozona)
    print("przed:", przed)
    print("po   :", po)
    print("opis :", opis)
    assert len(zlozona) == DLUGOSC
    assert po["CCAAT"] >= przed["CCAAT"] + 4
    assert po["GGCTAA"] >= 2
    print("OK")
