#!/usr/bin/env python3
"""E03 -- naturalne promotory Trichoderma jako drugi punkt startowy.

Patrz PLAN.md. Jedyny zbior w projekcie, ktory NIE pochodzi z modelu.

    python eksperymenty/E03_naturalne_promotory/run.py [--bez-chimer]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import (  # noqa: E402
    klient, kandydaci as K, metryki as M, zapisz,
)
from hyppe import seq as S  # noqa: E402

TU = Path(__file__).resolve().parent
OKNO_TATA = (720, 770)   # -80..-30 od TSS
K_MER = 4


def profil_kmerow(sekw: str, k: int = K_MER) -> dict[str, int]:
    s = sekw.upper()
    return dict(Counter(s[i:i + k] for i in range(len(s) - k + 1)
                        if set(s[i:i + k]) <= set("ACGT")))


def konsensus(sekwencje: list[str], od: int, do: int) -> dict:
    """Czestosci zasad na kazdej pozycji okna [od, do] (1-based, wlacznie)."""
    kolumny = []
    for p in range(od, do + 1):
        c = Counter(s[p - 1] for s in sekwencje if len(s) >= p and s[p - 1] in "ACGT")
        suma = sum(c.values()) or 1
        kolumny.append({
            "poz": p,
            "czestosci": {z: round(c.get(z, 0) / suma, 4) for z in "ACGT"},
            "dominujaca": max("ACGT", key=lambda z: c.get(z, 0)),
            "n": suma,
        })
    return {
        "od": od, "do": do,
        "kolumny": kolumny,
        "konsensus": "".join(k["dominujaca"] for k in kolumny),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bez-chimer", action="store_true")
    ap.add_argument("--bez-mapy", action="store_true",
                    help="pomin /mapa dla kazdego promotora (100 wywolan)")
    args = ap.parse_args()

    c = klient()
    dziki = c.dziki_seq()
    nat = K.wczytaj_naturalne()
    print(f"wczytano {len(nat)} naturalnych promotorow")

    dopelnione = [w for w in nat if w["dlugosc_oryginalna"] < 800]
    if dopelnione:
        print(f"UWAGA: {len(dopelnione)} krotszych niz 800 pz -- dopelnione 'N' "
              f"od strony 5' (kotwica na koncu 3', bo tam jest TSS)")

    rekordy = []
    for i, w in enumerate(nat, 1):
        s = w["sekwencja"]
        r = {
            "nazwa": w["nazwa"],
            "sekwencja": s,
            "dlugosc_oryginalna": w["dlugosc_oryginalna"],
            "gc": round(S.gc(s), 4),
            "sklad": S.sklad(s),
            "motywy": S.skanuj_motywy(s),
            "dystans_od_dzikiego": S.hamming(dziki, s),
            "kmery": profil_kmerow(s),
            "bije_dzikiego": c.lepsza(dziki, s),
        }
        if not args.bez_mapy:
            r["metryki"] = M.metryki_mapy(c.mapa(s))
        rekordy.append(r)
        if i % 10 == 0 or i == len(nat):
            print(f"  [{i:3d}/{len(nat)}] "
                  f"bijacych dzikiego: {sum(x['bije_dzikiego'] for x in rekordy)}")

    wygrywajace = [r for r in rekordy if r["bije_dzikiego"]]
    print(f"\nnaturalnych bijacych dzikiego: {len(wygrywajace)}/{len(rekordy)}")

    # --- konsensus okien: material dla czynnika C w E04
    seq_all = [r["sekwencja"] for r in rekordy]
    kons = {
        "rdzen": konsensus(seq_all, M.RDZEN_OD, M.RDZEN_DO),
        "okno_tata": konsensus(seq_all, *OKNO_TATA),
    }
    print(f"konsensus rdzenia 783-800 : {kons['rdzen']['konsensus']}")
    print(f"dziki      783-800        : {dziki[M.RDZEN_OD - 1:M.RDZEN_DO]}")
    print(f"konsensus 720-770         : {kons['okno_tata']['konsensus']}")

    # --- chimery: prawdziwe DNA po obu stronach ciecia
    chimery = []
    if not args.bez_chimer:
        # metryki bywaja puste (mapa liczona tylko dla podzbioru) -- None nie
        # da sie porownac, wiec sprowadzamy brak do wartosci sentinel.
        def _klucz(r):
            v = (r.get("metryki") or {}).get("blad_odtworzenia")
            return 999 if v is None else v

        rodzice = (wygrywajace or sorted(rekordy, key=_klucz))[:5]
        for r in rodzice:
            for ciecie, opis in ((M.RDZEN_OD - 1, "rdzen_od_naturalnego"),
                                 (M.RDZEN_DO, "rdzen_od_dzikiego"),
                                 (400, "polowa")):
                s = dziki[:ciecie] + r["sekwencja"][ciecie:]
                chimery.append({
                    "etykieta": f"chim_{r['nazwa'][:14]}_{opis}",
                    "rodzic": r["nazwa"], "ciecie": ciecie, "opis": opis,
                    "sekwencja": s,
                    "dystans_od_dzikiego": S.hamming(dziki, s),
                    "bije_dzikiego": c.lepsza(dziki, s),
                })
        print(f"chimery bijace dzikiego: "
              f"{sum(x['bije_dzikiego'] for x in chimery)}/{len(chimery)}")

    p = zapisz(TU / "wyniki.json", {
        "eksperyment": "E03_naturalne_promotory",
        "dziki": dziki,
        "k_mer": K_MER,
        "okno_rdzenia": [M.RDZEN_OD, M.RDZEN_DO],
        "okno_tata": list(OKNO_TATA),
        "rekordy": rekordy,
        "konsensus": kons,
        "chimery": chimery,
    })
    print(f"\nzapisano: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
