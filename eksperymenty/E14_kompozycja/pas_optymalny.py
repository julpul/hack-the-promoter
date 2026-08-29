#!/usr/bin/env python3
"""E14 -- v22: izolacja jedynej rodziny, ktorej nigdy nie testowalismy osobno.

Tabela naszych czterech ostatnich zgloszen w tym samym polu rankingowym:

    v14   45 x (blad 9-19) + 45 x (blad 0-9, dystans 123-171) + 10 kontroli   14,0
    v15  100 x (blad 10-17), jedna rodzina                                    12,0
    v16   45 x (blad 10-17) + 45 x (blad 0-11, dystans 192-262)               11,0
    w18   piec rodzin po 20, w tym kompozyty cis                              12,0

v15 nie mial rodziny "blad ~0", v16 mial ja za daleko. Jedyna konfiguracja,
ktora kiedykolwiek dala 14,0, zawiera **blad_odtworzenia bliski zeru przy
dystansie 123-171**. Ta rodzina nigdy nie stala sama na 100 slotach.

Roznica wobec v16 jest w punkcie startu, nie w liczbie pokolen: v14 szedl
z PLYTKICH ziaren v4 (blad 13-34), v16 z glebokich v15 (blad 10-17), i to
przesunelo cala rodzine o ~70 pz dalej od dzikiego. Tutaj wracamy do v4
i twardo tniemy po dystansie.

    python eksperymenty/E14_kompozycja/pas_optymalny.py [--maks-dystans 180]
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
WY = REPO / "runs" / "julian"
CEL = 100


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maks-dystans", type=int, default=180)
    ap.add_argument("--min-dystans", type=int, default=115)
    ap.add_argument("--watkow", type=int, default=24)
    ap.add_argument("--nazwa", default="v22_pas_optymalny")
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    rodzice = F.czytaj(WY / "v4.fasta")          # plytkie ziarna, jak w v14
    print(f"rodzicow (v4): {len(rodzice)}")
    t0 = time.time()

    def linia(arg):
        """Dwa pokolenia z jednego rodzica; zbieramy KAZDY krok, nie tylko ostatni."""
        i, r = arg
        out, biezaca = [], r.seq
        for pokolenie in (2, 3):
            wybor = None
            for kodow in (16, 24, 8):     # jak w v14 -- niskie kody = male kroki
                try:
                    e = c.edycje(biezaca, poziom=2, ile_kodow=kodow, opcji=8,
                                 ziarno=970_000 + i * 30 + pokolenie * 7 + kodow)
                except Exception:                            # noqa: BLE001
                    continue
                wybor = next((o["sekwencja"] for o in e["opcje"]
                              if c.lepsza(dziki, o["sekwencja"])), None)
                if wybor:
                    break
            if wybor is None:
                break
            biezaca = wybor
            d = S.hamming(dziki, biezaca)
            if d > a.maks_dystans:
                break                      # poza pasem -- dalej nie idziemy
            m = c.mapa(biezaca, 0, 800)
            out.append({"sekwencja": biezaca, "pokolenie": pokolenie,
                        "blad_odtworzenia": m["blad_odtworzenia"], "dystans": d})
        return out

    linie = rownolegle(linia, list(enumerate(rodzice)), watkow=a.watkow,
                       na_blad=[])
    pula = []
    for g in linie:
        pula.extend(g or [])
    print(f"wariantow surowo: {len(pula)}, {time.time()-t0:.0f}s")

    w_pasie = [x for x in pula
               if a.min_dystans <= x["dystans"] <= a.maks_dystans]
    print(f"w pasie dystansu {a.min_dystans}-{a.maks_dystans}: {len(w_pasie)}")

    # W pasie sortujemy po glebokosci: rodzina v14 miala blad 0-4-9.
    w_pasie.sort(key=lambda x: x["blad_odtworzenia"])
    wybor = w_pasie[:CEL]
    if len(wybor) < CEL:                      # dopelniamy tym, co poza pasem
        reszta = sorted((x for x in pula if x not in wybor),
                        key=lambda x: (x["blad_odtworzenia"], x["dystans"]))
        wybor += reszta[:CEL - len(wybor)]

    if wybor:
        b = [x["blad_odtworzenia"] for x in wybor]
        d = [x["dystans"] for x in wybor]
        print(f"wybrane {len(wybor)}: blad {min(b)} - {int(st.median(b))} - {max(b)}"
              f" | dystans {min(d)} - {int(st.median(d))} - {max(d)}")
        print("   (v14 blok B: blad 0 - 4 - 9 | dystans 123 - 142 - 171)")

    rek = [F.Rekord(f"P_pok{x['pokolenie']}_b{x['blad_odtworzenia']:02d}"
                    f"_d{x['dystans']}_{i:03d}", x["sekwencja"])
           for i, x in enumerate(wybor)]
    # Awaryjne dopelnienie z v14, zeby nie oddac slotow jako zer.
    uzyte = {r.seq for r in rek}
    for r in F.czytaj(WY / "v14_glebokosc.fasta"):
        if len(rek) >= CEL:
            break
        if r.seq not in uzyte:
            uzyte.add(r.seq)
            rek.append(F.Rekord(f"D_v14_{len(rek):03d}", r.seq))

    raport = F.waliduj(rek)
    plik = WY / f"{a.nazwa}.fasta"
    F.zapisz(plik, raport.ok[:CEL])
    print("\n" + raport.podsumowanie())
    print(f"zapisano -> {plik}")

    (TU / "wyniki_pas.json").write_text(json.dumps({
        "eksperyment": "E14_pas_optymalny", "plik": f"{a.nazwa}.fasta",
        "pas": [a.min_dystans, a.maks_dystans],
        "surowo": len(pula), "w_pasie": len(w_pasie),
        "wybor": [{k: v for k, v in x.items() if k != "sekwencja"}
                  for x in wybor],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
