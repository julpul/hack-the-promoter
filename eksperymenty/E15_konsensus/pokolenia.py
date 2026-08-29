#!/usr/bin/env python3
"""E15d -- os pokolen. Atrybucja v14 + budowa v14_glebokosc_v2.

Rozdzielenie blokow v14 (nigdy nie zrobione) daje wynik, ktory zmienia plan:

    blok A  pokolenie 1, WYBRANE jako 45 najglebszych ze 138 (1600 losowan)
            blad_odtworzenia  9 - 17 - 19
    blok B  pokolenie 2/3, BEZ zadnej selekcji na glebokosc
            blad_odtworzenia  0 -  4 -  9

**44 z 45 sekwencji bloku B sa glebsze niz najglebsza sekwencja bloku A.**
Drugie przejscie przez dekoder daje za darmo wiecej glebokosci niz przesiew
1600 losowan pierwszego pokolenia. Przesiewanie mocniej na pokoleniu 1 goni
ogon, ktory pokolenie 2 podaje z reki.

Ten skrypt sprawdza, jak daleko to siega, i rozdziela dwa czynniki:

  * POKOLENIE   2, 3, 4, 5 -- kazde przejscie bramkowane Sedzia,
  * START       ziarno zwykle (v4) vs ziarno glebokie (v14 blok A).

Czynnik START jest kontrola do W20 ("liczy sie ziarno, nie operator")
przeniesiona o poziom wyzej: czy glebokosc startu przenosi sie na potomka,
czy kazda linia zbiega do tego samego dna niezaleznie od tego, skad wyszla.

    python eksperymenty/E15_konsensus/pokolenia.py [--linii 30] [--watkow 16]
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client, rownolegle  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"

POKOLEN = 5          # ciagniemy do pokolenia 5 (v14 doszedl do 3)
OPCJI = 4

_lock = threading.Lock()
_stan = {"n": 0}


def _tik(co_ile: int = 10) -> None:
    with _lock:
        _stan["n"] += 1
        n = _stan["n"]
    if n % co_ile == 0:
        print(f"    linii gotowych: {n}", flush=True)


def linia(c: Client, dziki: str, start: str, ramie: str, idx: int) -> list[dict]:
    """Prowadzi jedna linie rodowa przez kolejne pokolenia.

    Kazde pokolenie musi przejsc bramke Sedziego, zeby wejsc do puli --
    nie zbieramy sekwencji, ktore przestaly byc promotorem.
    """
    out, biezaca = [], start
    for pokolenie in range(2, POKOLEN + 1):
        try:
            e = c.edycje(biezaca, poziom=2, ile_kodow=16, opcji=OPCJI,
                         ziarno=950_000 + idx * 100 + pokolenie)
        except Exception:                                    # noqa: BLE001
            break
        wybor = next((o["sekwencja"] for o in e["opcje"]
                      if c.lepsza(dziki, o["sekwencja"])), None)
        if wybor is None:
            break                       # linia wygasla -- nic nie przeszlo bramki
        biezaca = wybor
        try:
            m = c.mapa(biezaca, 0, 800)
        except Exception:                                    # noqa: BLE001
            break
        out.append({"sekwencja": biezaca, "ramie": ramie, "linia": idx,
                    "pokolenie": pokolenie,
                    "blad_odtworzenia": m["blad_odtworzenia"],
                    "dystans": S.hamming(dziki, biezaca)})
    _tik()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--linii", type=int, default=30, help="linii na ramie")
    ap.add_argument("--watkow", type=int, default=16)
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    t0 = time.time()

    v4 = F.czytaj(WYJSCIE / "v4.fasta")
    v14 = F.czytaj(WYJSCIE / "v14_glebokosc.fasta")
    glebokie = [r for r in v14 if r.nazwa.startswith("A_gleb")]

    zadania = [(r.seq, "P_plytki_start", i) for i, r in enumerate(v4[:a.linii])]
    zadania += [(r.seq, "G_gleboki_start", 1000 + i)
                for i, r in enumerate(glebokie[:a.linii])]

    print(f"linii: {len(zadania)} ({a.linii} na ramie), pokolenia 2-{POKOLEN}")
    print(f"szacunek wywolan: ~{len(zadania) * (POKOLEN - 1) * 6}\n", flush=True)

    _stan["n"] = 0
    wyniki = rownolegle(lambda z: linia(c, dziki, z[0], z[1], z[2]),
                        zadania, watkow=a.watkow, na_blad=[])
    pula = [x for grupa in wyniki for x in (grupa or [])]
    print(f"\nzebrano {len(pula)} wariantow, {time.time() - t0:.0f}s\n")

    print("=" * 76)
    print("POKOLENIE x START -> GLEBOKOSC")
    print("=" * 76)
    print(f"{'ramie':<18} {'pok':>4} {'n':>4} {'blad: min-med-max':>22}"
          f" {'dystans (med)':>14}")
    tabela = []
    for ramie in ("P_plytki_start", "G_gleboki_start"):
        for pok in range(2, POKOLEN + 1):
            g = [x for x in pula if x["ramie"] == ramie and x["pokolenie"] == pok]
            if not g:
                continue
            b = [x["blad_odtworzenia"] for x in g]
            d = [x["dystans"] for x in g]
            tabela.append({"ramie": ramie, "pokolenie": pok, "n": len(g),
                           "blad_min": min(b), "blad_mediana": st.median(b),
                           "blad_max": max(b), "dystans_mediana": st.median(d)})
            print(f"{ramie:<18} {pok:>4} {len(g):>4} {min(b):>8}"
                  f" {st.median(b):>6.1f} {max(b):>6} {st.median(d):>14.0f}")

    print(f"\nodniesienie -- v14 blok A (pokolenie 1, przesiew 1600): 9 - 17 - 19")

    przezywalnosc = {}
    for ramie in ("P_plytki_start", "G_gleboki_start"):
        start_n = a.linii
        for pok in range(2, POKOLEN + 1):
            ile = sum(1 for x in pula if x["ramie"] == ramie
                      and x["pokolenie"] == pok)
            przezywalnosc[f"{ramie}_pok{pok}"] = ile
        print(f"\n{ramie}: przezywalnosc linii przez bramke")
        print("   " + "  ".join(
            f"pok{p}: {przezywalnosc[f'{ramie}_pok{p}']}/{start_n}"
            for p in range(2, POKOLEN + 1)))

    (TU / "pokolenia.json").write_text(json.dumps({
        "linii_na_ramie": a.linii, "pokolen": POKOLEN,
        "sekund": round(time.time() - t0),
        "tabela": tabela, "przezywalnosc": przezywalnosc,
        "pula": pula,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nzapisano -> {TU / 'pokolenia.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
