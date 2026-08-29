#!/usr/bin/env python3
"""Test offline calego lancucha E01 -> E05 na zamockowanym API.

Nie dotyka sieci i nie potrzebuje klucza. Sprawdza, ze:
  - kazdy run.py przechodzi do konca i zapisuje wyniki.json,
  - portfel.py produkuje DOKLADNIE 100 unikalnych sekwencji po 800 pz,
  - notebook buduje sie bez bledu.

Sens: kod eksperymentow ma sie wywrocic TU, a nie po zuzyciu okna 5 minut.

    python eksperymenty/test_offline.py

Pisze do data/promotory_100.csv TYLKO jesli pliku nie ma (atrapa 100 sekwencji)
oraz do runs/test/. Prawdziwych danych nie nadpisuje.
"""
from __future__ import annotations

import csv
import random
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hyppe import seq as S  # noqa: E402

R = random.Random(42)
DZIKI = "".join(R.choice("ACGT") for _ in range(800))
DZIKI = S.wstaw(DZIKI, "GCGGAG", 560)   # CreA na 560 -- czynnik B ma w co celowac


class MockClient:
    """Nasladuje hyppe.Client na tyle, zeby przepuscic logike eksperymentow."""

    def __init__(self):
        self.wywolan = {"mapa": 0, "edycje": 0, "sedzia": 0}

    def dziki_seq(self):
        return DZIKI

    def mapa(self, sekwencja, od=0, ile=800):
        self.wywolan["mapa"] += 1
        rng = random.Random(hash(sekwencja) & 0xFFFF)
        pozycje = []
        for i, z in enumerate(sekwencja, 1):
            waga = 0.95 + 0.05 * rng.random() if i >= 783 else 0.03 * rng.random()
            zmien = "."
            if i in (154, 287, 362, 430, 434, 648, 750, 754, 778) and rng.random() < 0.7:
                zmien = rng.choice([x for x in "ACGT" if x != z])
            pozycje.append({
                "poz": i, "wej": z, "rekon": int(rng.random() > 0.11),
                "warstwy": [int(rng.random() < 0.15), int(rng.random() < 0.4),
                            int(rng.random() < 0.6)],
                "zmien_na": zmien, "wagaP": round(waga, 3),
            })
        rek = sum(1 for p in pozycje if p["zmien_na"] != ".")
        return {
            "naglowek": {
                "gatunek": "Trichoderma atroviride P1", "gatunek_kod": "P1",
                "rekon_frakcja": 0.88, "nie_rekonstruuje": 80 + rng.randint(0, 20),
                "zmian_pod_gatunek": rek, "blad_odtworzenia": 70 + rng.randint(0, 30),
                "warstwy_nazwy": ["L1", "L2", "L3"],
                "rozklad_warstw": {"0": 64, "1": 609, "2": 76, "3": 51}, "legenda": {},
            },
            "pozycje": pozycje,
        }

    def edycje(self, sekwencja, poziom=2, ile_kodow=8, opcji=8, ziarno=None):
        self.wywolan["edycje"] += 1
        rng = random.Random((ziarno or 0) * 977 + poziom * 13 + ile_kodow)
        return {"opcje": [
            {"nr": n + 1,
             "sekwencja": S.mutuj(sekwencja, ile=90 + ile_kodow,
                                  rng=random.Random(rng.random()))}
            for n in range(opcji)]}

    def lepsza(self, a, b):
        self.wywolan["sedzia"] += 1
        return (hash(b) ^ hash(a)) % 5 == 0          # ~20 % wygranych

    def zastosuj_rekomendacje(self, sekwencja, mapa=None):
        m = mapa if mapa is not None else self.mapa(sekwencja)
        out = list(sekwencja)
        for w in m["pozycje"]:
            if w["zmien_na"] != ".":
                out[w["poz"] - 1] = w["zmien_na"]
        return "".join(out)


def atrapa_csv() -> bool:
    """Tworzy data/promotory_100.csv TYLKO jesli go nie ma. Zwraca: czy stworzono."""
    p = REPO / "data" / "promotory_100.csv"
    if p.exists():
        return False
    p.parent.mkdir(exist_ok=True)
    rng = random.Random(7)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["nazwa", "gatunek", "sekwencja"])
        for i in range(100):
            dl = rng.choice([800, 800, 800, 750, 900])
            w.writerow([f"atrapa_{i:03d}", f"T. sp{i % 19}",
                        "".join(rng.choice("ACGT") for _ in range(dl))])
    return True


def main() -> int:
    stworzono = atrapa_csv()
    if stworzono:
        print("UWAGA: data/promotory_100.csv nie istnialo -- uzyto ATRAPY.")
        print("       Przed prawdziwym uruchomieniem podmien na plik z hackathonu.\n")

    mc = MockClient()
    problemy: list[str] = []

    import eksperymenty.E01_funkcja_celu.run as e1
    import eksperymenty.E02_artefakt_wagap.run as e2
    import eksperymenty.E03_naturalne_promotory.run as e3
    import eksperymenty.E04_blok_kombinacyjny.run as e4
    import eksperymenty.E05_portfel.portfel as e5

    for mod in (e1, e2, e3, e4, e5):
        mod.klient = lambda **kw: mc

    stary = sys.argv
    for nazwa, mod, argv in (("E01", e1, ["run"]), ("E02", e2, ["run"]),
                             ("E03", e3, ["run"]), ("E04", e4, ["run", "--replik", "2"])):
        sys.argv = argv
        try:
            mod.main()
            print(f"  {nazwa}: OK")
        except Exception as exc:  # noqa: BLE001
            problemy.append(f"{nazwa}: {type(exc).__name__}: {exc}")
            print(f"  {nazwa}: BLAD -- {exc}")

    wyj = REPO / "runs" / "test" / "v_test.fasta"
    sys.argv = ["portfel", "-o", str(wyj)]
    try:
        e5.main()
    except Exception as exc:  # noqa: BLE001
        problemy.append(f"E05: {type(exc).__name__}: {exc}")
        print(f"  E05: BLAD -- {exc}")
    sys.argv = stary

    from hyppe import fasta as F
    if wyj.exists():
        rek = F.czytaj(wyj)
        rap = F.waliduj(rek)
        print(f"\n=== PORTFEL ===\n{rap.podsumowanie()}")
        if len(rek) != 100:
            problemy.append(f"portfel ma {len(rek)} sekwencji zamiast 100")
        if rap.odrzucone:
            problemy.append(f"portfel: {len(rap.odrzucone)} odrzuconych przez walidacje")
        bloki: dict[str, int] = {}
        for r in rek:
            bloki[r.nazwa.split("_")[0]] = bloki.get(r.nazwa.split("_")[0], 0) + 1
        print("rozklad po blokach:", dict(sorted(bloki.items())))
        if len(bloki) < 8:
            problemy.append(f"tylko {len(bloki)} blokow -- portfel jest za malo rozny")
    else:
        problemy.append("portfel nie powstal")

    r = subprocess.run([sys.executable, str(REPO / "eksperymenty" / "zbuduj_notebook.py")],
                       capture_output=True, text=True)
    print("\n=== NOTEBOOK ===\n" + (r.stdout or r.stderr).strip())
    if r.returncode != 0:
        problemy.append("zbuduj_notebook.py zwrocil blad")

    print(f"\nwywolania API (zamockowane): {mc.wywolan}")
    print("\n" + "=" * 62)
    if problemy:
        print("PROBLEMY:")
        for p in problemy:
            print("  -", p)
        return 1
    print("WSZYSTKO OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
