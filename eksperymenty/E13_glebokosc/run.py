#!/usr/bin/env python3
"""E13 -- pchniecie osi, ktora JAKO JEDYNA dala duzy zysk.

Przejscie przez dekoder to jedyna interwencja z duzym efektem:
dziki 5,0 pkt -> ziarna 14,0 pkt (piec pozycji rankingu). Wszystkie dodatki
nakladane pozniej (CCAAT, gatunek, poli-AT, tandem, CreA, swiatlo) mieszcza
sie w pasmie 12-14, czyli w szumie wokol plateau.

Dwa nieprzetestowane sposoby pchniecia TEJ SAMEJ osi dalej:

  A GLEBOKOSC   -- ziarna wybieramy bramka binarna, nigdy po `blad_odtworzenia`.
                   Rozrzut na naszych 100 ziarnach: 13-21-34. Bierzemy skrajny
                   kwantyl (najglebiej na rozmaitosci modelu).
  B POKOLENIE   -- nasze ziarna leza 102-133 od dzikiego. Nie sprawdzilismy,
                   co jest na 150-250 wzdluz kierunku dekodera. Drugie i trzecie
                   pokolenie leza wlasnie tam.
  K KONTROLA    -- 10 obecnych ziaren z v4, zeby wynik dalo sie odczytac.

Zastrzezenie metodyczne: W18 pokazal, ze `blad_odtworzenia` nie przewiduje
werdyktu Sedziego (d = +0,06). Ale Sedzia jest WYSYCONY -- nie szereguje
niczego powyzej progu. Brak korelacji z Sedzia nie jest dowodem co do
Wyroczni. Ta sama pulapka co przy edycjach gatunkowych.

    python eksperymenty/E13_glebokosc/run.py [--losowan 1200]
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"
NAZWA = "v14_glebokosc"

POZIOMY = (1, 2)              # poziom 0 dal 0/48 trafien (W21)
ILE_KODOW = (8, 16, 24, 32)   # ile_kodow=4 jest martwe (W21)
N_A, N_B, N_K = 45, 45, 10


def przesiew(c: Client, dziki: str, budzet: int) -> list[dict]:
    """Losuje kandydatow, przepuszcza przez bramke, mierzy glebokosc."""
    kandydaci, losowan, nr = [], 0, 700_000
    while losowan < budzet:
        for poziom in POZIOMY:
            for ile_kodow in ILE_KODOW:
                if losowan >= budzet:
                    break
                nr += 1
                try:
                    e = c.edycje(dziki, poziom=poziom, ile_kodow=ile_kodow,
                                 opcji=8, ziarno=nr)
                except Exception as err:                     # noqa: BLE001
                    print(f"  [pominieto] {type(err).__name__}", flush=True)
                    continue
                for o in e["opcje"]:
                    losowan += 1
                    if not c.lepsza(dziki, o["sekwencja"]):
                        continue
                    m = c.mapa(o["sekwencja"], od=0, ile=800)
                    kandydaci.append({
                        "sekwencja": o["sekwencja"],
                        "blad_odtworzenia": m["blad_odtworzenia"],
                        "dystans": S.hamming(dziki, o["sekwencja"]),
                        "poziom": poziom, "ile_kodow": ile_kodow,
                    })
                if losowan % 200 < 8:
                    print(f"  losowan {losowan}/{budzet}, "
                          f"przez bramke {len(kandydaci)}", flush=True)
    return kandydaci


def pokolenia(c: Client, dziki: str, ziarna: list[F.Rekord],
              ile: int) -> list[dict]:
    """Drugie i trzecie przejscie przez dekoder -- dalej wzdluz kierunku."""
    out = []
    for i, z in enumerate(ziarna):
        if len(out) >= ile:
            break
        biezaca, pokolenie = z.seq, 1
        for _ in range(2):
            pokolenie += 1
            try:
                e = c.edycje(biezaca, poziom=2, ile_kodow=16, opcji=4,
                             ziarno=800_000 + i * 10 + pokolenie)
            except Exception:                                # noqa: BLE001
                break
            wybor = next((o["sekwencja"] for o in e["opcje"]
                          if c.lepsza(dziki, o["sekwencja"])), None)
            if wybor is None:
                break
            biezaca = wybor
            m = c.mapa(biezaca, od=0, ile=800)
            out.append({
                "sekwencja": biezaca, "pokolenie": pokolenie,
                "blad_odtworzenia": m["blad_odtworzenia"],
                "dystans": S.hamming(dziki, biezaca),
            })
        if (i + 1) % 15 == 0:
            print(f"  pokolenia: {i+1} ziaren -> {len(out)} wariantow", flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--losowan", type=int, default=1200)
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    ziarna_v4 = F.czytaj(WYJSCIE / "v4.fasta")

    print("=== BLOK A: przesiew na glebokosc ===")
    pula = przesiew(c, dziki, a.losowan)
    pula.sort(key=lambda x: x["blad_odtworzenia"])
    blok_a = pula[:N_A]
    print(f"  przez bramke {len(pula)} z {a.losowan}"
          f" ({100*len(pula)/a.losowan:.1f} %)")
    if pula:
        b = [x["blad_odtworzenia"] for x in pula]
        print(f"  blad_odtworzenia w puli: {min(b)} – {int(st.median(b))} – {max(b)}")
        print(f"  wybrane (najglebsze {N_A}): "
              f"{blok_a[0]['blad_odtworzenia']} – {blok_a[-1]['blad_odtworzenia']}")

    print("\n=== BLOK B: dalsze pokolenia ===")
    blok_b = pokolenia(c, dziki, ziarna_v4[:40], N_B)
    if blok_b:
        d = [x["dystans"] for x in blok_b]
        print(f"  wariantow {len(blok_b)}, dystans od dzikiego "
              f"{min(d)} – {int(st.median(d))} – {max(d)}")

    rekordy = [F.Rekord(f"A_gleb{x['blad_odtworzenia']:02d}_{i:03d}", x["sekwencja"])
               for i, x in enumerate(blok_a)]
    rekordy += [F.Rekord(f"B_pok{x['pokolenie']}_d{x['dystans']}_{i:03d}", x["sekwencja"])
                for i, x in enumerate(blok_b[:N_B])]
    rekordy += [F.Rekord(f"K_kontrola_{i:03d}", z.seq)
                for i, z in enumerate(ziarna_v4[:N_K])]

    raport = F.waliduj(rekordy)
    plik = WYJSCIE / f"{NAZWA}.fasta"
    F.zapisz(plik, raport.ok[:100])
    print("\n" + raport.podsumowanie())
    print(f"zapisano -> {plik}")

    (TU / "wyniki.json").write_text(json.dumps({
        "eksperyment": "E13_glebokosc", "plik": f"{NAZWA}.fasta",
        "losowan": a.losowan, "przez_bramke": len(pula),
        "blok_A": [{k: v for k, v in x.items() if k != "sekwencja"} for x in blok_a],
        "blok_B": [{k: v for k, v in x.items() if k != "sekwencja"} for x in blok_b],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
