#!/usr/bin/env python3
"""E02 -- czy szczyt wagaP idzie za trescia, czy siedzi na krawedzi wejscia?

Patrz PLAN.md. Rozstrzygajaca kontrola to ROTACJA: zachowuje cala tresc
lokalna i przesuwa ja wzgledem krawedzi.

    python eksperymenty/E02_artefakt_wagap/run.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import (  # noqa: E402
    klient, kandydaci as K, metryki as M, zapisz,
)

TU = Path(__file__).resolve().parent
ROTACJE = (100, 200, 400, 600)


def zbuduj_baterie(dziki: str) -> list[dict]:
    b: list[dict] = []

    def dodaj(etyk, grupa, sekw, **extra):
        b.append({"etykieta": etyk, "grupa": grupa, "sekwencja": sekw, **extra})

    dodaj("dziki", "odniesienie", dziki)

    # ROZSTRZYGAJACE: rotacja zachowuje tresc, przesuwa pozycje.
    # Oryginalny rdzen 783-800 ladauje po rotacji o k w okolicy 783-k (mod 800).
    for k in ROTACJE:
        dodaj(f"rotacja_{k}", "rotacja", K.obroc(dziki, k),
              rotacja=k,
              oczekiwany_szczyt=K.gdzie_po_rotacji(791, k),
              rdzen_po=[K.gdzie_po_rotacji(M.RDZEN_OD, k),
                        K.gdzie_po_rotacji(M.RDZEN_DO, k)])

    dodaj("odwrocony", "odwrocenie", K.odwroc(dziki), oczekiwany_szczyt=800 - 791 + 1)

    # Kontrola tresci: ten sam sklad, zero struktury.
    for z in (1, 2, 3):
        dodaj(f"przetasowany_{z}", "permutacja", K.przetasuj(dziki, ziarno=z))

    # Kontrola zerowa.
    for z in (1, 2, 3):
        dodaj(f"losowa_{z}", "losowa", K.losowa(ziarno=z))

    # Test lokalny: niszczymy TYLKO rdzen, reszta bez zmian.
    for z in (1, 2):
        dodaj(f"rdzen_losowy_{z}", "rdzen_zniszczony",
              K.podmien_okno(dziki, M.RDZEN_OD, M.RDZEN_DO, ziarno=z))
    dodaj("rdzen_poliA", "rdzen_zniszczony",
          K.podmien_okno(dziki, M.RDZEN_OD, M.RDZEN_DO,
                         wypelniacz="A" * (M.RDZEN_DO - M.RDZEN_OD + 1)))

    # Materialy: prawdziwe promotory (nie rozstrzygaja same z siebie -- patrz PLAN).
    try:
        for w in K.wczytaj_naturalne()[:10]:
            dodaj(f"nat_{w['nazwa'][:18]}", "naturalny", w["sekwencja"])
    except FileNotFoundError as e:
        print(f"  [pominieto naturalne] {e}", file=sys.stderr)

    return b


def main() -> int:
    c = klient()
    dziki = c.dziki_seq()
    bateria = zbuduj_baterie(dziki)
    print(f"bateria: {len(bateria)} sekwencji "
          f"(w tym {len(ROTACJE)} rotacji -- to one rozstrzygaja)")

    rekordy = []
    for i, poz in enumerate(bateria, 1):
        odp = c.mapa(poz["sekwencja"])
        m = M.metryki_mapy(odp)
        rekordy.append({
            **{k: v for k, v in poz.items() if k != "sekwencja"},
            "sekwencja": poz["sekwencja"],
            "metryki": m,
            "profil_wagaP": M.profil_wagap(odp),   # potrzebny do nakladki profili
        })
        ocz = poz.get("oczekiwany_szczyt")
        print(f"  [{i:2d}/{len(bateria)}] {poz['etykieta']:<24} "
              f"argmax={m['argmax']:>3} srodek_masy={m['srodek_masy']:>6} "
              f"masa_rdzenia={m['masa_rdzenia']}"
              + (f"  (oczekiwany szczyt {ocz})" if ocz else ""))

    # Skrot werdyktu juz w konsoli -- zeby nie czekac na notebook.
    print("\n--- szybki odczyt ---")
    rot = [r for r in rekordy if r["grupa"] == "rotacja"]
    if rot:
        zgodne = sum(1 for r in rot
                     if abs(r["metryki"]["argmax"] - r["oczekiwany_szczyt"]) < 60)
        na_koncu = sum(1 for r in rot if r["metryki"]["argmax"] >= 750)
        print(f"rotacje, szczyt poszedl za trescia : {zgodne}/{len(rot)}")
        print(f"rotacje, szczyt zostal na koncu    : {na_koncu}/{len(rot)}")
    perm = [r for r in rekordy if r["grupa"] in ("permutacja", "losowa")]
    if perm:
        na_koncu_p = sum(1 for r in perm if r["metryki"]["argmax"] >= 750)
        print(f"permutacje/losowe ze szczytem na koncu: {na_koncu_p}/{len(perm)}")
        print("   (jesli wysokie -> sygnal nie zalezy od tresci -> ARTEFAKT)")

    p = zapisz(TU / "wyniki.json", {
        "eksperyment": "E02_artefakt_wagap",
        "dziki": dziki,
        "rotacje": list(ROTACJE),
        "rdzen": [M.RDZEN_OD, M.RDZEN_DO],
        "rekordy": rekordy,
    })
    print(f"\nzapisano: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
