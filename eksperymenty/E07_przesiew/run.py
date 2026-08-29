#!/usr/bin/env python3
"""E07 -- gdzie w przestrzeni parametrow dekodera siedza ziarna przechodzace bramke.

Patrz PLAN.md. E06 pokazalo, ze potomek NIGDY nie bije rodzica (0/80), wiec
jedyna droga w gore jest lepsze ziarno, a jedyna droga do TOP10 -- wiele
NIEZALEZNYCH ziaren. Wgrane zglosznie mialo ich trzy.

    python eksperymenty/E07_przesiew/run.py [--opcji 8] [--na-ziarno 8]
"""

from __future__ import annotations

import argparse
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import klient, metryki as M, zapisz  # noqa: E402
from hyppe import fasta as F, seq as S  # noqa: E402

TU = Path(__file__).resolve().parent

POZIOMY = (0, 1, 2)
ILE_KODOW = (4, 8, 12, 16, 24, 32)
# mediana dystansu dziecko<->rodzic zmierzona w E06 (ramie R3/R5)
DYSTANS_CHMURY = 19
# ponizej tego progu dwie sekwencje uznajemy za to samo ziarno
PROG_ZIARNA = 40


def efektywne_ziarna(sekwencje: list[str], prog: int = PROG_ZIARNA) -> list[list[int]]:
    """Skupienia jednospojnikowe po dystansie Hamminga -> lista list indeksow.

    Odpowiada na pytanie "ile mamy NIEZALEZNYCH losowan", a nie "ile sekwencji".
    TOP10 to statystyka pozycyjna, wiec liczy sie ta pierwsza liczba (W11).
    """
    skupienia: list[list[int]] = []
    for i, s in enumerate(sekwencje):
        trafione = [k for k, sk in enumerate(skupienia)
                    if any(S.hamming(s, sekwencje[j]) < prog for j in sk)]
        if not trafione:
            skupienia.append([i])
            continue
        glowne = trafione[0]
        skupienia[glowne].append(i)
        for k in reversed(trafione[1:]):          # scal skupienia polaczone przez `i`
            skupienia[glowne] += skupienia.pop(k)
    return skupienia


def balans(c, dziki: str, wywolan: int, opcji: int, poziom: int = 2) -> int:
    """Zbalansowany test E07.2: kazda wartosc `ile_kodow` dostaje TYLE SAMO losowan.

    Etap 1b przesiewal wylacznie komorki, ktore trafily w siatce, wiec wynikajacy
    z niego trend wzdluz `ile_kodow` jest niepodwazalnie obciazony doborem proby.
    Tutaj n jest rowne dla wszystkich szesciu wartosci -- i dopiero to wolno
    porownywac. Bez tego W2 z fazy 1 ("ile_kodow nic nie steruje") zostaloby
    obalone na podstawie trzech trafien.
    """
    print(f"BALANS -- poziom={poziom}, {wywolan} wywolan x {opcji} opcji "
          f"na kazda z {len(ILE_KODOW)} wartosci ile_kodow")
    widziane: set[str] = set()
    komorki = []
    for ile_k in ILE_KODOW:
        n = trafien = 0
        for w in range(wywolan):
            odp = c.edycje(dziki, poziom=poziom, ile_kodow=ile_k, opcji=opcji,
                           ziarno=900_000 + ile_k * 1000 + w)
            for o in odp["opcje"]:
                s = o["sekwencja"]
                if s in widziane or s == dziki:
                    continue
                widziane.add(s)
                n += 1
                trafien += c.lepsza(dziki, s)
        komorki.append({"poziom": poziom, "ile_kodow": ile_k,
                        "n": n, "trafien": trafien})
        print(f"  ile_kodow {ile_k:>2}:  {trafien:>3}/{n:<4} ({trafien / n if n else 0:.1%})")

    p = zapisz(TU / "wyniki_balans.json", {
        "eksperyment": "E07_przesiew_balans", "poziom": poziom,
        "wywolan_na_komorke": wywolan, "opcji": opcji, "komorki": komorki})
    print(f"\nzapisano: {p}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--opcji", type=int, default=8, help="opcji na komorke siatki")
    ap.add_argument("--na-ziarno", type=int, default=8, help="wielkosc chmury na ziarno")
    ap.add_argument("--szeroki", type=int, default=0,
                    help="ile dodatkowych wywolan /edycje w komorkach, ktore trafiaja")
    ap.add_argument("--tylko-balans", type=int, default=0, metavar="WYWOLAN",
                    help="tylko zbalansowany test ile_kodow, N wywolan na wartosc")
    args = ap.parse_args()

    c = klient()
    dziki = c.dziki_seq()

    if args.tylko_balans:
        return balans(c, dziki, args.tylko_balans, args.opcji)

    # ── ETAP 1: siatka parametrow ──────────────────────────────────────────
    print("ETAP 1 -- siatka poziom x ile_kodow")
    siatka, wszystkie = [], []
    widziane: set[str] = set()
    for i, poziom in enumerate(POZIOMY):
        for j, ile_k in enumerate(ILE_KODOW):
            odp = c.edycje(dziki, poziom=poziom, ile_kodow=ile_k,
                           opcji=args.opcji, ziarno=3000 + i * 100 + j)
            trafien, n = 0, 0
            for o in odp["opcje"]:
                s = o["sekwencja"]
                if s in widziane or s == dziki:
                    continue
                widziane.add(s)
                bije = c.lepsza(dziki, s)
                n += 1
                trafien += bije
                wszystkie.append({"etykieta": f"p{poziom}k{ile_k}_{o['nr']}",
                                  "poziom": poziom, "ile_kodow": ile_k,
                                  "sekwencja": s, "bije_dzikiego": bije,
                                  "dystans_od_dzikiego": S.hamming(dziki, s)})
            siatka.append({"poziom": poziom, "ile_kodow": ile_k,
                           "n": n, "trafien": trafien})
            print(f"  poziom={poziom} ile_kodow={ile_k:>2}  "
                  f"{trafien}/{n} ({trafien / n if n else 0:.0%})")

    print(f"\n  lacznie {len(wszystkie)} sekwencji, "
          f"ziaren: {sum(x['bije_dzikiego'] for x in wszystkie)}")
    print("\n  odsetek trafien wg poziomu:")
    for p in POZIOMY:
        g = [x for x in siatka if x["poziom"] == p]
        t, n = sum(x["trafien"] for x in g), sum(x["n"] for x in g)
        print(f"    poziom {p}: {t}/{n} ({t / n if n else 0:.0%})")
    print("  odsetek trafien wg ile_kodow:")
    for k in ILE_KODOW:
        g = [x for x in siatka if x["ile_kodow"] == k]
        t, n = sum(x["trafien"] for x in g), sum(x["n"] for x in g)
        print(f"    ile_kodow {k:>2}: {t}/{n} ({t / n if n else 0:.0%})")

    # ── ETAP 1b: szeroki przesiew tam, gdzie siatka w ogole trafia ─────────
    # Odsetek trafien jest rzedu 2-6 %, wiec liczba ziaren jest ograniczona
    # LICZBA LOSOWAN, nie pomyslowoscia. Limity API (3000/min) tego nie ograniczaja.
    if args.szeroki:
        trafiajace = sorted({(x["poziom"], x["ile_kodow"]) for x in siatka
                             if x["trafien"]}) or [(1, 16), (2, 24), (2, 32)]
        print(f"\nETAP 1b -- szeroki przesiew, {args.szeroki} wywolan po {args.opcji} opcji")
        print(f"  komorki: {trafiajace}")
        for w in range(args.szeroki):
            poziom, ile_k = trafiajace[w % len(trafiajace)]
            odp = c.edycje(dziki, poziom=poziom, ile_kodow=ile_k,
                           opcji=args.opcji, ziarno=50_000 + w)
            for o in odp["opcje"]:
                s = o["sekwencja"]
                if s in widziane or s == dziki:
                    continue
                widziane.add(s)
                wszystkie.append({"etykieta": f"sz{w:03d}p{poziom}k{ile_k}_{o['nr']}",
                                  "poziom": poziom, "ile_kodow": ile_k,
                                  "sekwencja": s, "bije_dzikiego": c.lepsza(dziki, s),
                                  "dystans_od_dzikiego": S.hamming(dziki, s)})
            if (w + 1) % 10 == 0:
                print(f"  [{w + 1:3d}/{args.szeroki}] sekwencji {len(wszystkie)}, "
                      f"ziaren {sum(x['bije_dzikiego'] for x in wszystkie)}")

    ziarna = [x for x in wszystkie if x["bije_dzikiego"]]
    print(f"\n  RAZEM: {len(wszystkie)} sekwencji, ziaren {len(ziarna)} "
          f"({len(ziarna) / len(wszystkie):.1%})")

    if not ziarna:
        print("\nBRAK ZIAREN -- nie ma z czego budowac chmur.", file=sys.stderr)
        zapisz(TU / "wyniki.json", {"eksperyment": "E07_przesiew", "dziki": dziki,
                                    "siatka": siatka, "skan": wszystkie,
                                    "ziarna": [], "chmury": []})
        return 1

    # ── ETAP 2: ile z tych ziaren jest NIEZALEZNYCH ────────────────────────
    sk = efektywne_ziarna([z["sekwencja"] for z in ziarna])
    print(f"\nETAP 2 -- niezaleznosc ziaren (prog {PROG_ZIARNA} pz)")
    print(f"  {len(ziarna)} zwyciezcow -> {len(sk)} niezaleznych skupien")
    for nr, grupa in enumerate(sk):
        print(f"    skupienie {nr}: {len(grupa)} szt.  "
              f"{', '.join(ziarna[i]['etykieta'] for i in grupa[:4])}"
              f"{' ...' if len(grupa) > 4 else ''}")
    for nr, grupa in enumerate(sk):
        for i in grupa:
            ziarna[i]["skupienie"] = nr

    # ── ETAP 3: chmury wokol ziaren ────────────────────────────────────────
    print(f"\nETAP 3 -- chmury (perturbacja o {DYSTANS_CHMURY} pz, jak w E06/R5)")
    r = random.Random(7)
    chmury = []
    for z in ziarna:
        udane = 0
        for i in range(args.na_ziarno):
            s = S.mutuj(z["sekwencja"], ile=DYSTANS_CHMURY, rng=r)
            bije = c.lepsza(dziki, s)
            udane += bije
            chmury.append({"etykieta": f"{z['etykieta']}_c{i:02d}",
                           "ziarno": z["etykieta"], "skupienie": z.get("skupienie"),
                           "sekwencja": s, "bije_dzikiego": bije,
                           "bije_ziarna": c.lepsza(z["sekwencja"], s) if bije else False,
                           "dystans_od_dzikiego": S.hamming(dziki, s)})
        print(f"  {z['etykieta']:<16} chmura {udane}/{args.na_ziarno} "
              f"({udane / args.na_ziarno:.0%}) utrzymuje wygrana")

    wyd = [c_["bije_dzikiego"] for c_ in chmury]
    bije_ziarna = sum(c_["bije_ziarna"] for c_ in chmury)
    print(f"\n  wydajnosc chmur lacznie: {sum(wyd)}/{len(wyd)} ({st.mean(wyd):.0%})")
    print(f"  potomkow bijacych WLASNE ziarno: {bije_ziarna}/{len(chmury)}"
          f"   (E06 dal 0/80)")

    # ── wyjscie: wszystko, co przechodzi bramke, z atrybucja ziarna ────────
    przechodza = ([{"etykieta": f"E07z_{z['etykieta']}", "sekwencja": z["sekwencja"],
                    "skupienie": z.get("skupienie"), "rola": "ziarno"} for z in ziarna]
                  + [{"etykieta": f"E07c_{c_['etykieta']}", "sekwencja": c_["sekwencja"],
                      "skupienie": c_["skupienie"], "rola": "chmura"}
                     for c_ in chmury if c_["bije_dzikiego"]])
    fasta = TU / "zwyciezcy.fasta"
    F.zapisz(fasta, [(x["etykieta"], x["sekwencja"]) for x in przechodza])
    print(f"\n  przechodzacych bramke lacznie: {len(przechodza)} "
          f"z {len(sk)} niezaleznych skupien")

    # metryki mapy tylko dla ziaren -- do porownania z E01
    for z in ziarna:
        z["metryki"] = M.metryki_mapy(c.mapa(z["sekwencja"]))

    p = zapisz(TU / "wyniki.json", {
        "eksperyment": "E07_przesiew",
        "dziki": dziki,
        "poziomy": list(POZIOMY), "ile_kodow": list(ILE_KODOW),
        "prog_ziarna": PROG_ZIARNA, "dystans_chmury": DYSTANS_CHMURY,
        "siatka": siatka, "skan": wszystkie,
        "ziarna": ziarna, "skupienia": sk, "chmury": chmury,
        "przechodza_bramke": przechodza,
    })
    print(f"\nzapisano: {p}\n         {fasta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
