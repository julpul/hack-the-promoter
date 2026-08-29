#!/usr/bin/env python3
"""E14 -- ile jeszcze zostalo w osi glebokosci (rozwiniecie v14).

v14 dal +2,0 pkt, ale mial dwa parametry ustawione zachowawczo:

  * tylko 45 ze 100 slotow bylo blokiem glebokim (45 pokolen + 10 kontroli),
  * budzet 1600 losowan -> pula 138 -> najglebsze 45 to zakres 9-19.

Ten skrypt odkreca oba i dokłada pomiar, ktorego nigdy nie zrobilismy:
**czy `poziom` i `ile_kodow` wplywaja na `blad_odtworzenia`.** Dotad
mierzylismy ich wplyw wylacznie na dystans Hamminga (W21), co jest innym
pytaniem. Jesli ktoras kombinacja produkuje systematycznie glebsze ziarna,
to nie jest juz przesiew -- to jest strojenie zrodla.

    python eksperymenty/E14_kompozycja/przesiew.py [--losowan 6400] [--watkow 24]
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client, rownolegle  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"

# poziom 0 dal 0/48 trafien (W21), ile_kodow=4 jest martwe -- pomijamy.
# Gorny koniec ile_kodow rozszerzamy: 48 i 64 nie byly nigdy probowane.
POZIOMY = (1, 2)
ILE_KODOW = (8, 16, 24, 32, 48, 64)
OPCJI = 8


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--losowan", type=int, default=6400)
    ap.add_argument("--watkow", type=int, default=24)
    ap.add_argument("--nazwa", default="v15_czysta_glebokosc")
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    t0 = time.time()

    zadania, nr = [], 900_000
    while len(zadania) * OPCJI < a.losowan:
        for poziom in POZIOMY:
            for ile_kodow in ILE_KODOW:
                nr += 1
                zadania.append((poziom, ile_kodow, nr))

    print(f"faza 1/3: {len(zadania)} x /edycje = {len(zadania)*OPCJI} losowan",
          flush=True)
    partie = rownolegle(
        lambda z: (z, c.edycje(dziki, poziom=z[0], ile_kodow=z[1],
                               opcji=OPCJI, ziarno=z[2])),
        zadania, watkow=a.watkow)
    surowe = []
    for w in partie:
        if w is None:
            continue
        (poziom, ile_kodow, _), e = w
        for o in e["opcje"]:
            surowe.append({"sekwencja": o["sekwencja"],
                           "poziom": poziom, "ile_kodow": ile_kodow})
    print(f"  {len(surowe)} opcji, {time.time()-t0:.0f}s", flush=True)

    print("faza 2/3: bramka Sedziego", flush=True)
    werd = rownolegle(lambda x: c.lepsza(dziki, x["sekwencja"]),
                      surowe, watkow=a.watkow, na_blad=False)
    przez = [x for x, w in zip(surowe, werd) if w]
    print(f"  przez bramke {len(przez)} / {len(surowe)}"
          f" ({100*len(przez)/max(len(surowe),1):.1f} %), {time.time()-t0:.0f}s",
          flush=True)

    print("faza 3/3: glebokosc", flush=True)
    mapy = rownolegle(lambda x: c.mapa(x["sekwencja"], 0, 800),
                      przez, watkow=a.watkow)
    pula = [{**x, "blad_odtworzenia": m["blad_odtworzenia"],
             "dystans": S.hamming(dziki, x["sekwencja"])}
            for x, m in zip(przez, mapy) if m]
    pula.sort(key=lambda x: x["blad_odtworzenia"])
    print(f"  zmierzonych {len(pula)}, {time.time()-t0:.0f}s", flush=True)

    if not pula:
        print("pusta pula -- nic do zapisania")
        return 1

    # --- pomiar, ktorego nigdy nie zrobilismy: parametr -> glebokosc ---
    print("\n=== zrodlo: czy parametry steruja glebokoscia ===")
    print(f"{'poziom':>6} {'kodow':>6} {'przez':>6} {'n':>5} "
          f"{'blad min':>9} {'mediana':>8} {'dyst med':>9}")
    tabela = []
    for poziom in POZIOMY:
        for ile_kodow in ILE_KODOW:
            g = [x for x in pula if x["poziom"] == poziom
                 and x["ile_kodow"] == ile_kodow]
            proby = sum(1 for x in surowe if x["poziom"] == poziom
                        and x["ile_kodow"] == ile_kodow)
            if not g:
                print(f"{poziom:>6} {ile_kodow:>6} {0:>5.1f}% {0:>5}"
                      f" {'-':>9} {'-':>8} {'-':>9}")
                continue
            b = [x["blad_odtworzenia"] for x in g]
            d = [x["dystans"] for x in g]
            wiersz = {"poziom": poziom, "ile_kodow": ile_kodow,
                      "prob": proby, "przez": len(g),
                      "przelotowosc": round(100 * len(g) / max(proby, 1), 1),
                      "blad_min": min(b), "blad_mediana": st.median(b),
                      "dystans_mediana": st.median(d)}
            tabela.append(wiersz)
            print(f"{poziom:>6} {ile_kodow:>6} {wiersz['przelotowosc']:>5.1f}%"
                  f" {len(g):>5} {min(b):>9} {st.median(b):>8.1f}"
                  f" {st.median(d):>9.0f}")

    b = [x["blad_odtworzenia"] for x in pula]
    setka = pula[:100]
    print(f"\ncala pula     : blad {min(b)} - {st.median(b):.0f} - {max(b)}")
    print(f"najglebsze 100: blad {setka[0]['blad_odtworzenia']}"
          f" - {setka[-1]['blad_odtworzenia']}"
          f"   (v14, blok A 45 szt.: 9 - 19)")

    rekordy = [F.Rekord(f"G{x['blad_odtworzenia']:02d}_p{x['poziom']}"
                        f"k{x['ile_kodow']}_{i:03d}", x["sekwencja"])
               for i, x in enumerate(setka)]
    raport = F.waliduj(rekordy)
    plik = WYJSCIE / f"{a.nazwa}.fasta"
    F.zapisz(plik, raport.ok[:100])
    print("\n" + raport.podsumowanie())
    print(f"zapisano -> {plik}")

    (TU / "wyniki_przesiew.json").write_text(json.dumps({
        "eksperyment": "E14_przesiew", "plik": f"{a.nazwa}.fasta",
        "losowan": len(surowe), "przez_bramke": len(pula),
        "sekundy": round(time.time() - t0),
        "zrodlo": tabela,
        "pula": [{k: v for k, v in x.items() if k != "sekwencja"} for x in pula],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
