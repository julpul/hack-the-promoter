#!/usr/bin/env python3
"""Sklada v4.fasta: 100 sekwencji, kazda z INNEGO skupienia.

Uzasadnienie: TOP10 jest statystyka pozycyjna, wiec nagradza efektywna liczbe
niezaleznych prob (W20-W22). v1 mial 3 korzenie, v3 ma 56. Cel: 100.

Kolejnosc w pliku nie ma znaczenia dla oceny (serwer bierze pierwsze 100 po
filtrach), ale trzymamy ziarna przed chmurami, zeby przy niedoborze najpierw
wyleciala rodzina, a nie niezalezny los.

    python eksperymenty/E08_ziarna_do_100/zloz_portfel.py [-o runs/julian/v4.fasta]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
ZRODLA = [
    REPO / "eksperymenty" / "E08_ziarna_do_100" / "wyniki.json",
    REPO / "eksperymenty" / "E07_przesiew" / "wyniki.json",
]
PROG_SKUPIENIA = 40


def zbierz_ziarna() -> list[dict]:
    """Ziarna ze wszystkich przesiewow, odsiane do rozlacznych skupien."""
    wszystkie: list[dict] = []
    for zrodlo in ZRODLA:
        if not zrodlo.exists():
            print(f"  [brak] {zrodlo.name}")
            continue
        d = json.loads(zrodlo.read_text(encoding="utf-8"))
        z = [x for x in d.get("ziarna", []) if x.get("sekwencja")]
        print(f"  {zrodlo.parent.name}: {len(z)} ziaren")
        wszystkie += z

    # deduplikacja po skupieniu -- dwa przesiewy moga trafic w to samo miejsce
    wybrane: list[dict] = []
    odrzucone = 0
    for z in wszystkie:
        if all(S.hamming(z["sekwencja"], w["sekwencja"]) >= PROG_SKUPIENIA
               for w in wybrane):
            wybrane.append(z)
        else:
            odrzucone += 1
    print(f"  po deduplikacji skupien: {len(wybrane)} "
          f"(odrzucono {odrzucone} jako to samo skupienie)")
    return wybrane


def dopelnij_chmurami(ziarna: list[dict], cel: int) -> list[dict]:
    """Jesli ziaren < cel, dobiera rodzenstwo z E07 (chmury wokol ziaren)."""
    brak = cel - len(ziarna)
    if brak <= 0:
        return []
    e07 = REPO / "eksperymenty" / "E07_przesiew" / "wyniki.json"
    if not e07.exists():
        return []
    d = json.loads(e07.read_text(encoding="utf-8"))
    uzyte = {z["sekwencja"] for z in ziarna}
    chmury = [c for c in d.get("przechodza_bramke", [])
              if c.get("sekwencja") and c["sekwencja"] not in uzyte]
    print(f"  dopelnienie chmurami: {min(brak, len(chmury))} z {len(chmury)} dostepnych")
    return chmury[:brak]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="runs/julian/v4.fasta")
    ap.add_argument("--cel", type=int, default=100)
    a = ap.parse_args()

    print("zbieram ziarna:")
    ziarna = zbierz_ziarna()
    wybor = ziarna[:a.cel]
    dopelnienie = dopelnij_chmurami(wybor, a.cel)

    rekordy = [F.Rekord(f"z{i:03d}_{z.get('etykieta', 'ziarno')[:22]}", z["sekwencja"])
               for i, z in enumerate(wybor)]
    rekordy += [F.Rekord(f"c{i:03d}_{c.get('etykieta', 'chmura')[:22]}", c["sekwencja"])
                for i, c in enumerate(dopelnienie)]

    raport = F.waliduj(rekordy)
    out = REPO / a.out
    F.zapisz(out, raport.ok[:F.LIMIT_OCENIANYCH])

    print("\n" + raport.podsumowanie())
    print(f"\nsklad: {len(wybor)} niezaleznych ziaren + {len(dopelnienie)} z chmur")
    print(f"zapisano -> {out}")
    if len(wybor) < a.cel:
        print(f"UWAGA: tylko {len(wybor)} niezaleznych korzeni "
              f"-- TOP10 zobaczy tyle losowan, nie {a.cel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
