#!/usr/bin/env python3
"""E14 -- v16: struktura v14, ale kazdy blok podkrecony.

Pomiar, ktory to wymusil:

    v14  45 glebokich + 45 pokolen + 10 kontroli      14,0 pkt
    v15  100 x najglebsze (blad 10-17)                12,0 pkt

Czysta glebokosc jest GORSZA od mieszanki. Czyli nosnikiem zysku w v14 nie
byl ogon rozkladu `blad_odtworzenia` -- byl nim blok pokolen albo sama
roznorodnosc portfela. v16 trzyma wiec proporcje v14 i poprawia sklad
kazdego bloku osobno:

  A  45 najglebszych, ale z puli 603 kandydatow (v14 wybieral ze 138)
  B  45 pokolen startujacych z GLEBOKICH ziaren (v14 startowal z plytkich v4)
  K  10 sekwencji z v14 -- kontrola wzgledem naszego najlepszego pliku

Blok B jest tu jedyna realna niewiadoma, wiec dostaje najwiecej uwagi:
startujemy z ziaren juz przesianych na glebokosc, czego v14 nie robil.

    python eksperymenty/E14_kompozycja/pokolenia.py [--watkow 24]
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

N_A, N_B, N_K = 45, 45, 10
CEL = 100


def pokolenia(c: Client, dziki: str, rodzice: list[F.Rekord],
              watkow: int) -> list[dict]:
    """Dwa dalsze przejscia przez dekoder z kazdego rodzica.

    Parametry zrodla wziete z pomiaru w `przesiew.py`: poziom=2 z wysokim
    `ile_kodow` ma 15-16 % przelotowosci przez bramke wobec 3-9 % dla
    poziom=1 i niskich kodow. v14 losowal po calej siatce, w tym po
    cwiartkach, ktore prawie nic nie przepuszczaja.
    """
    def linia(arg):
        i, rodzic = arg
        out, biezaca = [], rodzic.seq
        for pokolenie in (2, 3):
            wybor = None
            for kodow in (48, 32, 64):          # najlepsze wg przelotowosci
                try:
                    e = c.edycje(biezaca, poziom=2, ile_kodow=kodow, opcji=8,
                                 ziarno=950_000 + i * 20 + pokolenie * 3
                                 + kodow)
                except Exception:                            # noqa: BLE001
                    continue
                wybor = next((o["sekwencja"] for o in e["opcje"]
                              if c.lepsza(dziki, o["sekwencja"])), None)
                if wybor:
                    break
            if wybor is None:
                break
            biezaca = wybor
            m = c.mapa(biezaca, 0, 800)
            out.append({"sekwencja": biezaca, "pokolenie": pokolenie,
                        "blad_odtworzenia": m["blad_odtworzenia"],
                        "dystans": S.hamming(dziki, biezaca)})
        return out

    linie = rownolegle(linia, list(enumerate(rodzice)), watkow=watkow,
                       na_blad=[])
    out = []
    for g in linie:
        out.extend(g or [])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watkow", type=int, default=24)
    ap.add_argument("--nazwa", default="v16_mieszanka_podkrecona")
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    t0 = time.time()

    glebokie = F.czytaj(WYJSCIE / "v15_czysta_glebokosc.fasta")
    z_v14 = F.czytaj(WYJSCIE / "v14_glebokosc.fasta")
    print(f"wejscie: {len(glebokie)} glebokich (v15), {len(z_v14)} z v14")

    blok_a = glebokie[:N_A]
    print(f"\nBLOK A: {len(blok_a)} najglebszych z puli 603")

    print("BLOK B: pokolenia z GLEBOKICH ziaren (v14 startowal z plytkich)")
    surowe = pokolenia(c, dziki, glebokie[:50], a.watkow)
    # Preferujemy pokolenie 3 -- to jest najdalszy punkt osi, jaki mamy.
    surowe.sort(key=lambda x: (-x["pokolenie"], x["blad_odtworzenia"]))
    blok_b = surowe[:N_B]
    if blok_b:
        d = [x["dystans"] for x in blok_b]
        b = [x["blad_odtworzenia"] for x in blok_b]
        p3 = sum(1 for x in blok_b if x["pokolenie"] == 3)
        print(f"  {len(blok_b)} wariantow ({p3} x pokolenie 3), "
              f"dystans {min(d)} - {int(st.median(d))} - {max(d)}, "
              f"blad {min(b)} - {int(st.median(b))} - {max(b)}, "
              f"{time.time()-t0:.0f}s")

    rekordy = [F.Rekord(f"A_{r.nazwa}", r.seq) for r in blok_a]
    rekordy += [F.Rekord(f"B_pok{x['pokolenie']}_b{x['blad_odtworzenia']:02d}"
                         f"_d{x['dystans']}_{i:03d}", x["sekwencja"])
                for i, x in enumerate(blok_b)]
    rekordy += [F.Rekord(f"K_v14_{i:03d}", r.seq)
                for i, r in enumerate(z_v14[:N_K])]

    # Dopelnienie do 100 -- ALL100 dzieli zawsze przez 100.
    uzyte = {r.seq for r in rekordy}
    n = 0
    for zrodlo, prefiks in ((glebokie[N_A:], "D_gleb"), (z_v14[N_K:], "D_v14")):
        for r in zrodlo:
            if len(rekordy) >= CEL:
                break
            if r.seq in uzyte:
                continue
            uzyte.add(r.seq)
            n += 1
            rekordy.append(F.Rekord(f"{prefiks}_{n:03d}", r.seq))
    if n:
        print(f"  dopelniono {n} sekwencji do {CEL}")

    raport = F.waliduj(rekordy)
    plik = WYJSCIE / f"{a.nazwa}.fasta"
    F.zapisz(plik, raport.ok[:CEL])
    print("\n" + raport.podsumowanie())
    print(f"zapisano -> {plik}")

    (TU / "wyniki_pokolenia.json").write_text(json.dumps({
        "eksperyment": "E14_pokolenia", "plik": f"{a.nazwa}.fasta",
        "sekundy": round(time.time() - t0),
        "blok_B": [{k: v for k, v in x.items() if k != "sekwencja"}
                   for x in blok_b],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
