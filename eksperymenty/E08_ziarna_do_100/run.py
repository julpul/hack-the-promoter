#!/usr/bin/env python3
"""E08 -- dobierz ziarna do 100 niezaleznych skupien.

Uzasadnienie: W20 (liczy sie ziarno, nie operator), W21 (~8 % losowan trafia),
W22 (wgrane zgloszenie mialo 3 niezalezne losowania). TOP10 jest statystyka
pozycyjna, wiec nagradza EFEKTYWNA LICZBE NIEZALEZNYCH PROB. Maksymalizujemy
ja wprost: 100 ziaren, kazde z osobnego skupienia.

    python eksperymenty/E08_ziarna_do_100/run.py [--cel 100] [--budzet 1200]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client  # noqa: E402
from hyppe import seq as S  # noqa: E402

TU = Path(__file__).resolve().parent
E07 = TU.parent / "E07_przesiew" / "wyniki.json"
PROG_SKUPIENIA = 40          # ponizej tego dystansu = to samo skupienie (za E07)
POZIOMY = (1, 2)             # poziom 0 dal 0/48 trafien (W21)
ILE_KODOW = (8, 16, 24, 32)  # ile_kodow=4 jest martwe (W21)


def wczytaj_ziarna_e07() -> list[dict]:
    if not E07.exists():
        return []
    d = json.loads(E07.read_text(encoding="utf-8"))
    return [z for z in d.get("ziarna", []) if z.get("sekwencja")]


def nowe_skupienie(kandydat: str, ziarna: list[dict]) -> bool:
    return all(S.hamming(kandydat, z["sekwencja"]) >= PROG_SKUPIENIA for z in ziarna)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cel", type=int, default=100, help="docelowa liczba ziaren")
    ap.add_argument("--budzet", type=int, default=1200, help="maks. losowan")
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    ziarna = wczytaj_ziarna_e07()
    print(f"ziaren z E07: {len(ziarna)} | cel: {a.cel}")

    losowan = trafien = odrzuconych_bliskich = 0
    nr_ziarna = 90_000
    while len(ziarna) < a.cel and losowan < a.budzet:
        for poziom in POZIOMY:
            for ile_kodow in ILE_KODOW:
                if len(ziarna) >= a.cel or losowan >= a.budzet:
                    break
                nr_ziarna += 1
                try:
                    e = c.edycje(dziki, poziom=poziom, ile_kodow=ile_kodow,
                                 opcji=8, ziarno=nr_ziarna)
                except Exception as err:                      # noqa: BLE001
                    print(f"  [pominieto losowanie] {type(err).__name__}: {err}")
                    continue
                for o in e["opcje"]:
                    if len(ziarna) >= a.cel:
                        break
                    losowan += 1
                    s = o["sekwencja"]
                    if not c.lepsza(dziki, s):
                        continue
                    trafien += 1
                    if not nowe_skupienie(s, ziarna):
                        odrzuconych_bliskich += 1
                        continue
                    ziarna.append({
                        "etykieta": f"E08_sz{len(ziarna):03d}p{poziom}k{ile_kodow}",
                        "poziom": poziom, "ile_kodow": ile_kodow,
                        "ziarno": nr_ziarna, "sekwencja": s,
                        "dystans_od_dzikiego": S.hamming(dziki, s),
                        "bije_dzikiego": True, "zrodlo": "E08",
                    })
                    print(f"  +ziarno {len(ziarna):3d}/{a.cel}"
                          f"  (p{poziom} k{ile_kodow}, losowan {losowan},"
                          f" trafien {trafien})")

    wynik = {
        "eksperyment": "E08_ziarna_do_100",
        "prog_skupienia": PROG_SKUPIENIA,
        "losowan": losowan,
        "trafien": trafien,
        "odrzuconych_jako_to_samo_skupienie": odrzuconych_bliskich,
        "ziaren_lacznie": len(ziarna),
        "ziarna": ziarna,
    }
    (TU / "wyniki.json").write_text(json.dumps(wynik, ensure_ascii=False),
                                    encoding="utf-8")

    print(f"\nlosowan {losowan} | trafien {trafien}"
          f" ({100*trafien/max(losowan,1):.1f} %)"
          f" | odrzuconych jako to samo skupienie {odrzuconych_bliskich}")
    print(f"ziaren lacznie: {len(ziarna)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
