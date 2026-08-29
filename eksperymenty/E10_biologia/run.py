#!/usr/bin/env python3
"""E10 -- trzy portfele biologiczne wg PLAN_BIOLOGICZNY.md.

  B0  linia bazowa: 100 kopii dzikiego rozniacych sie o 1 podstawienie
      -> bez tego nie wiemy, czy cokolwiek poprawilismy (brak kontroli)
  B1  trakty poli(dA:dT): region wolny od nukleosomow przed TSS
      -> jedyna zmiana ruszajaca ARCHITEKTURE, nie tozsamosc pojedynczych zasad
  B2  chimery z pieciu promotorow szczepu P1 (nasz szczep docelowy)
      -> jedyny material z tego samego repertuaru czynnikow transkrypcyjnych

    python eksperymenty/E10_biologia/run.py [--portfel B0|B1|B2|wszystkie]
"""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hyppe import Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402
from eksperymenty.wspolne import kandydaci as K  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TU = Path(__file__).resolve().parent
WYJSCIE = REPO / "runs" / "julian"
CEL = 100
TSS = 800   # promotor wyrownany do miejsca startu transkrypcji


def trakty(s: str, minlen: int = 6) -> list[tuple[int, int]]:
    return [(m.start() + 1, len(m.group()))
            for m in re.finditer(r"A{%d,}|T{%d,}" % (minlen, minlen), s)]


# ─────────────────────────── B0 ───────────────────────────

def zbuduj_b0(dziki: str) -> list[F.Rekord]:
    """100 kopii dzikiego, kazda z DOKLADNIE jednym podstawieniem.

    Minimalna perturbacja pozwalajaca przejsc filtr unikalnosci. Odczyt mowi,
    ile punktow wart jest sam punkt wyjscia.
    """
    r = random.Random(31337)
    pozycje = r.sample(range(1, 801), CEL)
    out = []
    for i, p in enumerate(sorted(pozycje)):
        stara = dziki[p - 1]
        nowa = r.choice([z for z in "ACGT" if z != stara])
        out.append(F.Rekord(f"B0_{i:03d}_p{p}{stara}{nowa}",
                            dziki[:p - 1] + nowa + dziki[p:]))
    return out


# ─────────────────────────── B1 ───────────────────────────

def zbuduj_b1(dziki: str) -> list[F.Rekord]:
    """Trakty poli(dA:dT) tworzace region wolny od nukleosomow.

    Umiejscowienie: NFR u grzybow lezy tuz przed TSS. Ciezar rozkladu klademy
    na -50..-350 (pozycje 450-750), z czescia wariantow siegajaca dalej.
    Dlugosci 10-25 pz -- w zakresie obserwowanym w zbiorze naturalnym
    (najdluzszy trakt tam: 27 pz).
    """
    r = random.Random(4242)
    out = []
    for i in range(CEL):
        ile = 2 + (i % 7)                       # 2..8 traktow
        s = dziki
        uzyte: list[int] = []
        for _ in range(ile):
            for _proba in range(30):
                dl = r.randint(10, 25)
                # 70 % traktow w oknie proksymalnym, 30 % rozrzucone
                if r.random() < 0.7:
                    p = r.randint(450, 750 - dl)
                else:
                    p = r.randint(30, 780 - dl)
                if all(abs(p - u) > 30 for u in uzyte):
                    uzyte.append(p)
                    s = S.wstaw(s, r.choice("AT") * dl, p)
                    break
        out.append(F.Rekord(f"B1_{i:03d}_t{len(uzyte)}", s))
    return out


# ─────────────────────────── B2 ───────────────────────────

def zbuduj_b2(dziki: str) -> list[F.Rekord]:
    """Chimery dziki x promotory szczepu P1 (Trichoderma atroviride P1).

    Piec promotorow z NASZEGO szczepu to jedyny material w projekcie, ktory
    dzieli z genem docelowym repertuar czynnikow transkrypcyjnych.
    Dwa typy: jednopunktowa (wymiana konca) i przeszczep segmentu.
    """
    r = random.Random(99)
    nat = K.wczytaj_naturalne()
    p1 = [n for n in nat if n["nazwa"].startswith("P1_")]
    if not p1:
        raise SystemExit("brak promotorow P1_ w zbiorze naturalnym")
    print(f"  dawcy ze szczepu P1: {[n['nazwa'] for n in p1]}")

    out = []
    ciecia = [120, 200, 280, 360, 440, 520, 600, 660, 700, 740]
    # 50 chimer jednopunktowych: 5 dawcow x 10 ciec
    for dawca in p1:
        for ciecie in ciecia:
            out.append(F.Rekord(
                f"B2_1p_{dawca['nazwa'][:10]}_c{ciecie}",
                dziki[:ciecie] + dawca["sekwencja"][ciecie:]))
    # 50 przeszczepow segmentu: fragment dawcy wstawiony w dzikiego
    while len(out) < CEL:
        dawca = r.choice(p1)
        dlug = r.choice([80, 120, 160, 200, 250])
        start = r.randint(1, 800 - dlug)
        s = dziki[:start] + dawca["sekwencja"][start:start + dlug] + dziki[start + dlug:]
        out.append(F.Rekord(
            f"B2_seg_{dawca['nazwa'][:10]}_s{start}d{dlug}", s))
    return out[:CEL]


# ─────────────────────────── pomiar ───────────────────────────

def zapisz_i_zmierz(c: Client, dziki: str, rekordy: list[F.Rekord],
                    plik: str, probka: int = 15) -> dict:
    raport = F.waliduj(rekordy)
    sciezka = WYJSCIE / plik
    F.zapisz(sciezka, raport.ok[:CEL])
    seqs = [x.seq for x in raport.ok[:CEL]]

    r = random.Random(0)
    prob = r.sample(raport.ok[:CEL], min(probka, len(raport.ok)))
    bramka = sum(1 for x in prob if c.lepsza(dziki, x.seq))
    bledy = [c.mapa(x.seq, od=0, ile=800)["blad_odtworzenia"] for x in prob[:6]]

    info = {
        "plik": plik,
        "n": len(seqs),
        "dystans_od_dzikiego": [min(S.hamming(dziki, s) for s in seqs),
                                int(st.median([S.hamming(dziki, s) for s in seqs])),
                                max(S.hamming(dziki, s) for s in seqs)],
        "gc": [round(min(S.gc(s) for s in seqs), 3),
               round(st.median([S.gc(s) for s in seqs]), 3),
               round(max(S.gc(s) for s in seqs), 3)],
        "traktow_poliAT": [min(len(trakty(s)) for s in seqs),
                           int(st.median([len(trakty(s)) for s in seqs])),
                           max(len(trakty(s)) for s in seqs)],
        "bramka": f"{bramka}/{len(prob)}",
        "blad_odtworzenia": sorted(bledy),
    }
    print(f"  sekwencji           : {info['n']} (odrzuconych {len(raport.odrzucone)},"
          f" duplikatow {len(raport.duplikaty)})")
    print(f"  dystans od dzikiego : {info['dystans_od_dzikiego']} (min/med/max)")
    print(f"  GC                  : {info['gc']}")
    print(f"  traktow poli(dA:dT) : {info['traktow_poliAT']}")
    print(f"  bramka Sedziego     : {info['bramka']}")
    print(f"  blad_odtworzenia    : {info['blad_odtworzenia']}")
    print(f"  zapisano -> {sciezka}")
    return info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--portfel", default="wszystkie",
                    choices=["B0", "B1", "B2", "wszystkie"])
    a = ap.parse_args()

    c = Client.from_env()
    dziki = c.dziki_seq()
    print(f"dziki: GC {S.gc(dziki):.1%}, traktow poli(dA:dT) {len(trakty(dziki))}\n")
    wyniki = {}

    if a.portfel in ("B0", "wszystkie"):
        print("=== B0: linia bazowa (dziki +1 podstawienie) ===")
        wyniki["B0"] = zapisz_i_zmierz(c, dziki, zbuduj_b0(dziki),
                                       "v9_B0_linia_bazowa.fasta")
    if a.portfel in ("B1", "wszystkie"):
        print("\n=== B1: trakty poli(dA:dT) -- region wolny od nukleosomow ===")
        wyniki["B1"] = zapisz_i_zmierz(c, dziki, zbuduj_b1(dziki),
                                       "v10_B1_poliAT.fasta")
    if a.portfel in ("B2", "wszystkie"):
        print("\n=== B2: chimery z promotorami szczepu P1 ===")
        wyniki["B2"] = zapisz_i_zmierz(c, dziki, zbuduj_b2(dziki),
                                       "v11_B2_chimery_P1.fasta")

    (TU / "wyniki.json").write_text(
        json.dumps({"eksperyment": "E10_biologia", "portfele": wyniki},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nzapisano {TU / 'wyniki.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
