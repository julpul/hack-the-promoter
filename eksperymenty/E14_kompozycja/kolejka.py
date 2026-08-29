#!/usr/bin/env python3
"""Kolejkuje wgrania co `--odstep` sekund i loguje wyniki do JSON.

Okno /wgraj to 5 min. Reczne czekanie miedzy zgloszeniami marnuje okna, gdy
mamy kilka gotowych plikow -- ten skrypt wysyla je po kolei i zapisuje wynik
kazdego, zeby dalo sie je porownac w jednej tabeli.

Serwer trzyma NAJLEPSZE zgloszenie po surowym TOP10 (potwierdzone: `v11`
dal 4,0 i nasz znacznik w rankingu sie nie ruszyl), wiec kazde wgranie jest
darmowym pomiarem.

    python eksperymenty/E14_kompozycja/kolejka.py plik1.fasta plik2.fasta ...
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import ApiError, Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
LOG = TU / "wyniki_wgran.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pliki", nargs="+")
    ap.add_argument("--odstep", type=int, default=305)
    a = ap.parse_args()

    c = Client.from_env()
    log = json.loads(LOG.read_text()) if LOG.exists() else []

    for nr, sciezka in enumerate(a.pliki):
        p = Path(sciezka)
        if not p.is_absolute():
            p = REPO / p
        raport = F.waliduj(F.czytaj(p))
        if len(raport.ok) < 100:
            print(f"[pomijam] {p.name}: tylko {len(raport.ok)} sekwencji",
                  flush=True)
            continue
        tekst = F.na_tekst(raport.ok[:100])

        for proba in range(12):
            try:
                r = c.wgraj(tekst)
                break
            except ApiError as e:
                if e.kod != 429:
                    raise
                print(f"  429, czekam 45 s ({p.name})", flush=True)
                time.sleep(45)
        else:
            print(f"[porazka] {p.name}: nie udalo sie wgrac", flush=True)
            continue

        wpis = {"plik": p.name,
                "czas": time.strftime("%H:%M:%S"),
                "top10": r.get("pozycja_top10"),
                "top100": r.get("pozycja_top100"),
                "punkty": r.get("punkty_razem"),
                "ocenionych": r.get("ocenionych")}
        log.append(wpis)
        LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        print(f"{wpis['czas']}  {p.name:32s} TOP10={wpis['top10']} "
              f"ALL100={wpis['top100']}  punkty={wpis['punkty']}", flush=True)

        if nr < len(a.pliki) - 1:
            time.sleep(a.odstep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
