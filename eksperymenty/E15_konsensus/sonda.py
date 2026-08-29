#!/usr/bin/env python3
"""E15c -- pomiar konsensusu i drabiny odszumiania. ~40 wywolan API.

Analiza offline dala dwa wyniki:

  1. Konsensus 100 ziaren NIE wraca do dzikiego. Lezy 91 pz od niego,
     a w kazdej z tych 91 kolumn dziki jest w mniejszosci (czesto 0/100).
     Dekoder ma wiec silna skladowa SYSTEMATYCZNA: ziarno = konsensus + ~51 pz
     wlasnego szumu.
  2. Ale dystans do konsensusu NIE przewiduje glebokosci w bloku A
     (Pearson -0,08). Zastrzezenie: blok A byl wybrany jako najglebszy,
     wiec zakres glebokosci jest sciety do 9-19. Ograniczenie zakresu tlumi
     korelacje -- to nie jest dowod na brak zaleznosci.

Rozstrzyga pomiar bezposredni. Mierzymy:

  * konsensus globalny i konsensusy blokowe (A/B/K),
  * DRABINE ODSZUMIANIA: ziarno przyciagane do konsensusu w 0/25/50/75/100 %
    jego wlasnych pozycji idiosynkratycznych. Jesli glebokosc rosnie wzdluz
    drabiny, odszumianie jest nowa dzwignia; jesli spada, ziarna sa glebokie
    WLASNIE dzieki wlasnemu szumowi i konsensus jest slepa uliczka.

Drabina jest wazniejsza niz sam konsensus, bo daje kierunek, a nie punkt.

    python eksperymenty/E15_konsensus/sonda.py
"""

from __future__ import annotations

import json
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client, rownolegle  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WATKOW = 8          # skromnie -- rownolegle chodzi przesiew v15
DRABINA = (0.0, 0.25, 0.50, 0.75, 1.0)
ZIAREN_NA_DRABINE = 6


def przyciagnij(ziarno: str, kon: str, frakcja: float, rng: random.Random) -> str:
    """Zastepuje `frakcja` pozycji idiosynkratycznych ziarna zasada konsensusu.

    Pozycje idiosynkratyczne = te, w ktorych ziarno rozni sie od konsensusu.
    frakcja=0 -> ziarno bez zmian; frakcja=1 -> dokladnie konsensus.
    """
    rozne = [i for i in range(len(ziarno)) if ziarno[i] != kon[i]]
    if not rozne or frakcja <= 0:
        return ziarno
    ile = round(frakcja * len(rozne))
    out = list(ziarno)
    for i in rng.sample(rozne, min(ile, len(rozne))):
        out[i] = kon[i]
    return "".join(out)


def main() -> int:
    dane = json.loads((TU / "konsensus.json").read_text(encoding="utf-8"))
    kon = dane["konsensus"]
    per_blok = dane["konsensus_per_blok"]

    c = Client.from_env()
    dziki = c.dziki_seq()
    rek = F.czytaj(REPO / "runs" / "julian" / "v14_glebokosc.fasta")
    blok_a = [r for r in rek if r.nazwa.startswith("A_gleb")]

    # --- 1. konsensusy ---
    kandydaci = [("konsensus_global", kon), ("dziki", dziki)]
    kandydaci += [(f"konsensus_blok_{b}", s) for b, s in per_blok.items()]
    kandydaci += [(blok_a[0].nazwa, blok_a[0].seq),      # najglebsze ziarno (9)
                  (blok_a[-1].nazwa, blok_a[-1].seq)]    # najplytsze z bloku A

    # --- 2. drabina odszumiania ---
    rng = random.Random(20260829)
    ziarna = blok_a[:ZIAREN_NA_DRABINE]
    drabina = []
    for z in ziarna:
        for f in DRABINA:
            s = przyciagnij(z.seq, kon, f, rng)
            drabina.append((z.nazwa, f, s))
    kandydaci += [(f"drab_{n}_f{int(f*100):03d}", s) for n, f, s in drabina]

    print(f"pomiar {len(kandydaci)} sekwencji ({WATKOW} watkow)\n", flush=True)

    mapy = rownolegle(lambda t: c.mapa(t[1], 0, 800), kandydaci, watkow=WATKOW)
    bramka = rownolegle(lambda t: c.lepsza(dziki, t[1]), kandydaci,
                        watkow=WATKOW, na_blad=None)

    wyniki = {}
    for (nazwa, s), m, b in zip(kandydaci, mapy, bramka):
        wyniki[nazwa] = {
            "blad_odtworzenia": m["blad_odtworzenia"] if m else None,
            "bije_dzikiego": b,
            "do_dzikiego": S.hamming(dziki, s),
            "do_konsensusu": S.hamming(kon, s),
        }

    print("=" * 76)
    print("1. KONSENSUSY -- czy srodek rozmaitosci jest glebszy niz jej punkty")
    print("=" * 76)
    print(f"{'sekwencja':<26} {'blad':>6} {'bramka':>8} {'do dzik':>8} {'do kons':>8}")
    for nazwa in ("dziki", "konsensus_global", "konsensus_blok_A",
                  "konsensus_blok_B", "konsensus_blok_K",
                  blok_a[0].nazwa, blok_a[-1].nazwa):
        w = wyniki.get(nazwa)
        if not w:
            continue
        print(f"{nazwa:<26} {str(w['blad_odtworzenia']):>6}"
              f" {str(w['bije_dzikiego']):>8} {w['do_dzikiego']:>8}"
              f" {w['do_konsensusu']:>8}")

    print()
    print("=" * 76)
    print("2. DRABINA ODSZUMIANIA -- ziarno -> konsensus")
    print("=" * 76)
    print(f"{'frakcja':>8} {'n':>3} {'blad: min-mediana-max':>26} {'bramka':>10}"
          f" {'do kons (med)':>14}")
    tabela = []
    for f in DRABINA:
        grupa = [wyniki[f"drab_{n}_f{int(f*100):03d}"] for n, ff, _ in drabina
                 if ff == f]
        b = [g["blad_odtworzenia"] for g in grupa if g["blad_odtworzenia"] is not None]
        przez = sum(1 for g in grupa if g["bije_dzikiego"])
        dk = [g["do_konsensusu"] for g in grupa]
        if not b:
            continue
        tabela.append({"frakcja": f, "n": len(b), "blad_min": min(b),
                       "blad_mediana": st.median(b), "blad_max": max(b),
                       "przez_bramke": przez, "do_konsensusu": st.median(dk)})
        print(f"{f:>8.2f} {len(b):>3} {min(b):>10} {st.median(b):>7.1f}"
              f" {max(b):>7} {przez:>6}/{len(grupa):<3} {st.median(dk):>14.0f}")

    print("\nodczyt:")
    print("  blad SPADA wzdluz drabiny -> odszumianie poglebia, konsensus wygrywa")
    print("  blad ROSNIE              -> szum wlasny ziarna jest czescia glebokosci")
    print("  bez zmian                -> glebokosc nie zalezy od tej osi")

    (TU / "sonda.json").write_text(json.dumps({
        "wyniki": wyniki, "drabina": tabela,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nzapisano -> {TU / 'sonda.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
