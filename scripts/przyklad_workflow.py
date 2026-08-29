#!/usr/bin/env python3
"""Przyklad pelnego workflow z poziomu kodu (nie CLI).

Pokazuje wzorzec, ktory bedziemy automatyzowac:
    dziki -> pula kandydatow -> selekcja Sedzia -> FASTA -> wgraj

    python scripts/przyklad_workflow.py --strategia hybryda --ile 100
    python scripts/przyklad_workflow.py --wgraj      # faktycznie wysyla
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hyppe import Client, strategie  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe.config import REPO_ROOT  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategia", default="nawigator", choices=sorted(strategie.REJESTR))
    ap.add_argument("--ile", type=int, default=100)
    ap.add_argument("--rund", type=int, default=4, help="rund turnieju szwajcarskiego")
    ap.add_argument("--kto", default="wspolne", help="podkatalog w runs/ (zeby sobie nie nadpisywac)")
    ap.add_argument("--wgraj", action="store_true")
    a = ap.parse_args()

    c = Client.from_env()

    # 1. punkt wyjscia
    dziki = c.dziki_seq()
    print(f"dziki: {len(dziki)} pz")

    # 2. pula kandydatow
    pula = strategie.uruchom(a.strategia, c, dziki, ile=a.ile)
    print(f"pula '{a.strategia}': {len(pula)} kandydatow")

    # 3. selekcja: kto przebija dzikiego + kolejnosc wg turnieju
    wygrane = c.turniej(dziki, pula)
    print(f"przebilo dzikiego: {len(wygrane)}/{len(pula)}")

    uszeregowane = c.ranking_swiss(dict(wygrane) or pula, rund=a.rund)
    print("top 5 wg Sedziego:")
    for etyk, pkt, _ in uszeregowane[:5]:
        print(f"   {etyk:<20} {pkt} zwyciestw")

    # 4. plik: najlepsze na poczatku, reszta puli dopelnia do 100
    najlepsze = [(e, s) for e, _, s in uszeregowane]
    uzyte = {s for _, s in najlepsze}
    dopelnienie = [(e, s) for e, s in pula.items() if s not in uzyte]
    rekordy = (najlepsze + dopelnienie)[: F.LIMIT_OCENIANYCH]

    raport = F.waliduj([F.Rekord(e, s) for e, s in rekordy])
    out = REPO_ROOT / "runs" / a.kto / f"{a.strategia}.fasta"
    F.zapisz(out, raport.ok)
    print("\n" + raport.podsumowanie())
    print(f"zapisano -> {out}")

    # 5. zgloszenie
    if a.wgraj:
        wynik = c.wgraj(F.na_tekst(raport.ok))
        print("wgrane:", {k: wynik.get(k) for k in
                          ("ocenionych", "pozycja_top10", "pozycja_top100", "punkty_razem")})
    else:
        print(f"\n(dry) wyslij:  python -m hyppe wgraj {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
