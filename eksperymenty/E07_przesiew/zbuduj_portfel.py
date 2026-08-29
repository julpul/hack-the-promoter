#!/usr/bin/env python3
"""Portfel z przesiewu: 100 NIEZALEZNYCH ziaren przechodzacych bramke.

Uzasadnienie w E06/PLAN.md i E07/PLAN.md, w skrocie:

  * potomek praktycznie nigdy nie bije rodzica (1 przypadek na 494),
    wiec chmura wokol ziarna nie podnosi maksimum -- tylko je powiela;
  * TOP10 jest statystyka pozycyjna, wiec liczy sie liczba NIEZALEZNYCH
    losowan, a nie liczba sekwencji (W11);
  * wgrane zgloszenie ma 39 sekwencji przechodzacych bramke, ale pochodza
    one z TRZECH ziaren -- czyli to trzy losowania, nie trzydziesci dziewiec.

Stad portfel, w ktorym kazda ze stu sekwencji jest osobnym ziarnem.
Dobierane sa wylacznie sekwencje przechodzace bramke i oddalone od siebie
o co najmniej `--prog` pz, zeby "niezalezne" znaczylo cos sprawdzalnego.

    python eksperymenty/E07_przesiew/zbuduj_portfel.py -o runs/julian/v3.fasta
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import REPO, klient, wczytaj, zapisz  # noqa: E402
from hyppe import fasta as F, seq as S  # noqa: E402

TU = Path(__file__).resolve().parent

# Zbalansowany test (wyniki_balans.json): ile_kodow=4 daje 0/96, reszta 5-11 %
# w granicach szumu. Wiec: cokolwiek >= 8, poziom > 0. Parametry nie steruja
# trafieniami -- steruje nimi liczba losowan.
USTAWIENIA = [(p, k) for p in (1, 2) for k in (8, 12, 16, 24, 32)]


def daleko_od_wszystkich(s: str, zbior: list[str], prog: int) -> bool:
    return all(S.hamming(s, x) >= prog for x in zbior)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--wyjscie", default=str(REPO / "runs" / "julian" / "v3.fasta"))
    ap.add_argument("--cel", type=int, default=100)
    ap.add_argument("--prog", type=int, default=40, help="min. dystans miedzy ziarnami")
    ap.add_argument("--opcji", type=int, default=8)
    ap.add_argument("--max-wywolan", type=int, default=400)
    args = ap.parse_args()

    c = klient()
    dziki = c.dziki_seq()

    wybrane: list[tuple[str, str]] = []       # (etykieta, sekwencja)
    sekw: list[str] = []

    # 1. zaczynamy od ziaren juz zmierzonych w E07 -- nie placimy za nie drugi raz
    w = wczytaj(TU / "wyniki.json")
    for z in (w or {}).get("ziarna", []):
        if len(wybrane) >= args.cel:
            break
        if daleko_od_wszystkich(z["sekwencja"], sekw, args.prog) and not F.problemy(z["sekwencja"]):
            wybrane.append((f"E07_{z['etykieta']}", z["sekwencja"]))
            sekw.append(z["sekwencja"])
    print(f"z zapisanych wynikow E07: {len(wybrane)} niezaleznych ziaren")

    # 2. dosiewamy, az bedzie `cel` ziaren
    wywolan = odrzucone_blisko = 0
    while len(wybrane) < args.cel and wywolan < args.max_wywolan:
        poziom, ile_k = USTAWIENIA[wywolan % len(USTAWIENIA)]
        odp = c.edycje(dziki, poziom=poziom, ile_kodow=ile_k, opcji=args.opcji,
                       ziarno=700_000 + wywolan)
        wywolan += 1
        for o in odp["opcje"]:
            if len(wybrane) >= args.cel:
                break
            s = o["sekwencja"]
            if s in sekw or F.problemy(s) or not c.lepsza(dziki, s):
                continue
            if not daleko_od_wszystkich(s, sekw, args.prog):
                odrzucone_blisko += 1
                continue
            wybrane.append((f"E07d_p{poziom}k{ile_k}_{wywolan:03d}_{o['nr']}", s))
            sekw.append(s)
        if wywolan % 20 == 0:
            print(f"  [{wywolan:3d} wywolan] ziaren {len(wybrane)}/{args.cel}")

    print(f"\nziaren: {len(wybrane)}  (dosiew: {wywolan} wywolan /edycje, "
          f"{odrzucone_blisko} odrzuconych jako zbyt bliskie)")

    if len(wybrane) < args.cel:
        # Awaryjnie: dopelniamy chmurami. Sa skorelowane z ziarnem, wiec dla TOP10
        # sa warte mniej -- ale przechodza bramke, wiec dla ALL100 licza sie tak samo.
        brak = args.cel - len(wybrane)
        print(f"UWAGA: brakuje {brak} ziaren -> dopelniam chmurami (skorelowane!)")
        for ch in (w or {}).get("chmury", []):
            if len(wybrane) >= args.cel:
                break
            if ch["bije_dzikiego"] and ch["sekwencja"] not in sekw \
                    and not F.problemy(ch["sekwencja"]):
                wybrane.append((f"E07c_{ch['etykieta']}", ch["sekwencja"]))
                sekw.append(ch["sekwencja"])

    rap = F.waliduj([F.Rekord(n, s) for n, s in wybrane[:args.cel]])
    print("\n" + rap.podsumowanie())

    # ile z tego to naprawde niezalezne losowania
    niezalezne = []
    for _, s in wybrane[:args.cel]:
        if daleko_od_wszystkich(s, niezalezne, args.prog):
            niezalezne.append(s)
    print(f"niezaleznych losowan w portfelu: {len(niezalezne)}/{len(rap.ok[:args.cel])}")

    p = Path(args.wyjscie)
    F.zapisz(p, [(r.nazwa, r.seq) for r in rap.ok[:args.cel]])
    zapisz(TU / "portfel_v3.json", {
        "eksperyment": "E07_portfel_v3", "cel": args.cel, "prog": args.prog,
        "niezaleznych": len(niezalezne), "wywolan_dosiewu": wywolan,
        "sekwencje": [{"etykieta": n, "sekwencja": s} for n, s in wybrane[:args.cel]],
    })
    print(f"\nzapisano: {p}  ({len(rap.ok[:args.cel])} sekwencji)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
