#!/usr/bin/env python3
"""Wgrywa kolejne pliki, czekajac na okno 5 minut miedzy zgloszeniami.

    python eksperymenty/E09_trzy_taktyki/wgraj_kolejno.py plik1.fasta plik2.fasta

Kazde zgloszenie jest pomiarem: liczy sie najlepszy wynik druzyny, wiec
gorsze zgloszenie niczego nie psuje -- kosztuje tylko okno.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import ApiError, Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent


def czekaj_na_okno(c: Client) -> None:
    while True:
        czekaj = c.me().get("zgloszenie_mozliwe_za_s") or 0
        if czekaj <= 0:
            return
        print(f"  okno zajete jeszcze {czekaj} s -- czekam", flush=True)
        time.sleep(min(czekaj + 2, 60))


def main() -> int:
    pliki = sys.argv[1:]
    if not pliki:
        return print("podaj pliki do wgrania") or 1

    c = Client.from_env()
    zebrane = []
    for sciezka in pliki:
        p = REPO / sciezka if not Path(sciezka).is_absolute() else Path(sciezka)
        raport = F.waliduj(F.czytaj(p))
        if len(raport.ok) < 100:
            print(f"POMIJAM {p.name}: tylko {len(raport.ok)} poprawnych sekwencji")
            continue

        czekaj_na_okno(c)
        print(f"\nwgrywam {p.name} ...", flush=True)
        try:
            r = c.wgraj(F.na_tekst(raport.ok[:100]))
        except ApiError as e:
            print(f"  BLAD {e.kod}: {e.tresc}", flush=True)
            continue
        wpis = {"plik": p.name,
                "pozycja_top10": r.get("pozycja_top10"),
                "pozycja_top100": r.get("pozycja_top100"),
                "punkty_razem": r.get("punkty_razem"),
                "ocenionych": r.get("ocenionych")}
        zebrane.append(wpis)
        print(f"  TOP10 poz. {wpis['pozycja_top10']} | "
              f"ALL100 poz. {wpis['pozycja_top100']} | "
              f"punkty {wpis['punkty_razem']}", flush=True)

    (TU / "wgrania.json").write_text(json.dumps(zebrane, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    print("\n=== podsumowanie zgloszen ===")
    for w in zebrane:
        print(f"  {w['plik']:<32} TOP10 {w['pozycja_top10']} | "
              f"ALL100 {w['pozycja_top100']} | {w['punkty_razem']} pkt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
