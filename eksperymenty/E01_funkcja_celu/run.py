#!/usr/bin/env python3
"""E01 -- czy naglowek /nawigator/mapa zawiera porownywalny skalar?

Patrz PLAN.md. Zbiera bateria 28 sekwencji, dla kazdej pobiera mape i werdykt
Sedziego, zapisuje wszystko do wyniki.json.

    python eksperymenty/E01_funkcja_celu/run.py [--bez-sedziego]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import (  # noqa: E402
    klient, kandydaci as K, metryki as M, zapisz,
)
from hyppe import seq as S  # noqa: E402

TU = Path(__file__).resolve().parent


def zbuduj_baterie(c, dziki: str, pelna_pula: bool = True) -> list[dict]:
    """[{etykieta, grupa, sekwencja, opis}] -- deterministycznie."""
    b: list[dict] = []

    def dodaj(etyk, grupa, sekw, opis=""):
        b.append({"etykieta": etyk, "grupa": grupa, "sekwencja": sekw, "opis": opis})

    dodaj("dziki", "odniesienie", dziki, "promotor wyjsciowy pks1")

    # --- determinizm: ta sama sekwencja pytana wielokrotnie (E01.3)
    for i in range(1, 5):
        dodaj(f"dziki_powt{i}", "powtorzenie", dziki, "ten sam dziki, kolejne wywolanie")

    # --- wariant gatunkowy: iteracja do punktu stalego (H7)
    biezaca = dziki
    for krok in (1, 2):
        biezaca = c.zastosuj_rekomendacje(biezaca)
        dodaj(f"gatunek_it{krok}", "gatunek", biezaca,
              f"rekomendacje zmien_na naniesione {krok}x, dystans "
              f"{S.hamming(dziki, biezaca)}")

    # --- istniejaca pula hybryda
    pula = K.wczytaj_pule(ile=8)
    for i, (nazwa, sekw) in enumerate(pula.items()):
        dodaj(f"pula_{i:02d}", "pula_hybryda", sekw, f"z runs/julian/pula.fasta: {nazwa}")

    # --- CALA wgrana pula: jedyne zrodlo WARIANCJI werdyktu Sedziego.
    # Na osmiu sekwencjach powyzej kazda przegrywa z dzikim, wiec E01.4 i E01.5
    # sa nietestowalne -- zmienna zalezna jest stala. Setka daje kilka wygranych
    # i dopiero wtedy pytanie "czy skalar przewiduje Sedziego" ma sens.
    if pelna_pula:
        for i, (nazwa, sekw) in enumerate(K.wczytaj_pule().items()):
            if sekw in {x["sekwencja"] for x in b}:
                continue
            dodaj(f"pelna_{i:03d}", "pula_pelna", sekw, f"pula.fasta: {nazwa}")

    # --- wyjscia dekodera, trzy poziomy latentu
    for poziom in (0, 1, 2):
        odp = c.edycje(dziki, poziom=poziom, ile_kodow=8, opcji=2, ziarno=101 + poziom)
        for j, o in enumerate(odp["opcje"][:2]):
            dodaj(f"dekoder_p{poziom}_{j}", "dekoder", o["sekwencja"],
                  f"/edycje poziom={poziom} ile_kodow=8")

    # --- KONTROLA MONOTONICZNOSCI: znane uporzadkowanie a priori
    for ile in (5, 50, 200):
        dodaj(f"losowe_{ile}", "kontrola_monotonicznosc",
              S.mutuj(dziki, ile=ile, ziarno=7),
              f"{ile} losowych podstawien -- wiemy, ze to pogorszenie")

    # --- dolne granice
    dodaj("przetasowany", "kontrola_dolna", K.przetasuj(dziki, ziarno=1),
          "ten sam sklad zasad, zniszczona kolejnosc")
    dodaj("losowa_gc", "kontrola_dolna", K.losowa(ziarno=1),
          "sekwencja losowa o GC dzikiego")

    # --- naturalne promotory (jesli plik jest)
    try:
        nat = K.wczytaj_naturalne()
        for w in nat[:2]:
            dodaj(f"naturalny_{w['nazwa'][:16]}", "naturalny", w["sekwencja"],
                  f"promotory_100.csv, oryginalnie {w['dlugosc_oryginalna']} pz")
    except FileNotFoundError as e:
        print(f"  [pominieto naturalne] {e}", file=sys.stderr)

    return b


def powtorz_sedziego(c, dziki: str, probki: list[tuple[str, str]], powtorzen: int) -> list[dict]:
    """Czy werdykt Sedziego jest POWTARZALNY dla tej samej pary sekwencji?

    Bez tego pomiaru zdanie "3 sekwencje na 45 bija dzikiego" jest nieinterpretowalne:
    trzy wygrane moga byc trzema realnymi zwyciezcami albo trzema rzutami monetą.
    Skalar z E01 porownujemy wlasnie z tym werdyktem, wiec jego szum jest gornym
    ograniczeniem na kazda korelacje, jaka da sie tu zmierzyc.
    """
    out = []
    for etyk, s in probki:
        w = [c.lepsza(dziki, s) for _ in range(powtorzen)]
        out.append({"etykieta": etyk, "werdykty": w, "wygranych": sum(w),
                    "n": powtorzen, "powtarzalny": len(set(w)) == 1})
        print(f"  {etyk:<26} {sum(w)}/{powtorzen} wygranych  "
              f"{'POWTARZALNY' if len(set(w)) == 1 else '*** NIEPOWTARZALNY ***'}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bez-sedziego", action="store_true",
                    help="pomin pojedynki (szybciej, ale bez E01.4/E01.5)")
    ap.add_argument("--bez-pelnej-puli", action="store_true",
                    help="tylko 8 sekwencji z puli zamiast wszystkich 100")
    ap.add_argument("--powtorzen-sedziego", type=int, default=8,
                    help="ile razy powtorzyc ten sam pojedynek (0 = pomin kontrole)")
    args = ap.parse_args()

    c = klient()
    dziki = c.dziki_seq()
    print(f"dziki: {len(dziki)} pz, GC {S.gc(dziki):.1%}")

    bateria = zbuduj_baterie(c, dziki, pelna_pula=not args.bez_pelnej_puli)
    print(f"bateria: {len(bateria)} sekwencji")

    rekordy = []
    for i, poz in enumerate(bateria, 1):
        odp = c.mapa(poz["sekwencja"])
        m = M.metryki_mapy(odp)
        m["dystans_od_dzikiego"] = S.hamming(dziki, poz["sekwencja"])
        m["gc"] = round(S.gc(poz["sekwencja"]), 4)

        if not args.bez_sedziego and poz["grupa"] != "powtorzenie":
            m["bije_dzikiego"] = c.lepsza(dziki, poz["sekwencja"])
        else:
            m["bije_dzikiego"] = None

        rekordy.append({**{k: v for k, v in poz.items() if k != "sekwencja"},
                        "sekwencja": poz["sekwencja"], "metryki": m})
        if poz["grupa"] != "pula_pelna" or m["bije_dzikiego"]:
            print(f"  [{i:3d}/{len(bateria)}] {poz['etykieta']:<26} "
                  f"blad_odtw={m.get('blad_odtworzenia')} "
                  f"zmian_gat={m.get('zmian_pod_gatunek')} "
                  f"srodek_masy={m.get('srodek_masy')} "
                  f"bije={m['bije_dzikiego']}")
        elif i % 25 == 0:
            print(f"  [{i:3d}/{len(bateria)}] ... pula_pelna, "
                  f"wygranych do tej pory: "
                  f"{sum(1 for r in rekordy if r['metryki']['bije_dzikiego'])}")

    # --- KONTROLA: czy Sedzia w ogole jest powtarzalny?
    # Probki dobierane PO pomiarze, zeby trafic na realnych zwyciezcow i przegranych,
    # a nie na to, co uznalismy za zwyciezcow przed pomiarem.
    powt_sedziego = []
    if args.powtorzen_sedziego and not args.bez_sedziego:
        wygrane = [r for r in rekordy if r["metryki"]["bije_dzikiego"] is True]
        przegrane = [r for r in rekordy if r["metryki"]["bije_dzikiego"] is False]
        probki = [(r["etykieta"], r["sekwencja"]) for r in wygrane[:3]]
        probki += [(r["etykieta"], r["sekwencja"]) for r in przegrane[:3]]
        probki.append(("dziki_vs_dziki", dziki))   # kontrola remisu
        print(f"\npowtarzalnosc Sedziego ({args.powtorzen_sedziego} powtorzen na pare):")
        powt_sedziego = powtorz_sedziego(c, dziki, probki, args.powtorzen_sedziego)

    p = zapisz(TU / "wyniki.json", {
        "eksperyment": "E01_funkcja_celu",
        "dziki": dziki,
        "rekordy": rekordy,
        "pola_kandydujace": list(M.POLA_NAGLOWKA),
        "powtarzalnosc_sedziego": powt_sedziego,
    })
    print(f"\nzapisano: {p}")
    print("teraz: python eksperymenty/zbuduj_notebook.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
