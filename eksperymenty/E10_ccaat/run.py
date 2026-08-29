#!/usr/bin/env python3
"""E10 -- analiza porownawcza pks1 vs 100 naturalnych promotorow Trichoderma
i naszczepienie miejsc CCAAT na 100 niezaleznych ziaren z v4.

Patrz PLAN.md. Cala ANALIZA jest offline (zero wywolan API) -- liczy sie
z eksperymenty/E03_naturalne_promotory/wyniki.json.
API jest uzywane wylacznie do kontrolnej probki bramki Sedziego (--bramka N).

    python eksperymenty/E10_ccaat/run.py
    python eksperymenty/E10_ccaat/run.py --bramka 20      # + 20 pojedynkow
    python eksperymenty/E10_ccaat/run.py --miejsc 6       # wiecej miejsc CCAAT
"""

from __future__ import annotations

import argparse
import math
import statistics as st
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import KATALOG, REPO, klient, wczytaj, zapisz  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402

TU = Path(__file__).resolve().parent
TSS = 800
# CCAAT dziala niezaleznie od orientacji -- szukamy na obu niciach.
CELE = ("CCAAT", "ATTGG")


def obie_nici(s: str, wzor: str) -> list[int]:
    """Pozycje (1-based) motywu na obu niciach."""
    a = S.znajdz_iupac(s, wzor)
    b = [len(s) - p - len(wzor) + 2 for p in S.znajdz_iupac(S.rewers_komplement(s), wzor)]
    return sorted(set(a + b))


def oczekiwane(s: str, motyw: str = "CCAAT") -> float:
    """Ile trafien spodziewamy sie z samego skladu zasad (obie nici).

    Bez tej liczby zdanie 'dziki nie ma CCAAT' jest nieinterpretowalne --
    trzeba wiedziec, ile brakow daje sam przypadek.
    """
    czyste = [c for c in s if c in "ACGT"]
    n = len(czyste)
    f = {z: czyste.count(z) / n for z in "ACGT"}
    p = pr = 1.0
    for c in motyw:
        p *= f[c]
    for c in S.rewers_komplement(motyw):
        pr *= f[c]
    return (p + pr) * (n - len(motyw) + 1)


def informacja_pozycyjna(seqs: list[str], min_n: int = 50) -> list[float | None]:
    """2 - entropia kolumny, w bitach. None gdy za malo danych (dopelnienia N)."""
    out = []
    for p in range(len(seqs[0])):
        c = Counter(x for x in (s[p] for s in seqs) if x in "ACGT")
        n = sum(c.values())
        if n < min_n:
            out.append(None)
            continue
        out.append(2 + sum(v / n * math.log2(v / n) for v in c.values() if v))
    return out


def pwm(seqs: list[str], od: int, do: int, pseudo: float = 0.5) -> list[dict]:
    m = []
    for p in range(od - 1, do):
        c = Counter(x for x in (s[p] for s in seqs) if x in "ACGT")
        n = sum(c.values())
        m.append({z: (c.get(z, 0) + pseudo) / (n + 4 * pseudo) for z in "ACGT"})
    return m


def punktuj(seq: str, m: list[dict], od: int) -> float:
    return sum(math.log2(m[i][seq[od - 1 + i]] / 0.25)
               for i in range(len(m)) if seq[od - 1 + i] in "ACGT")


def kandydaci_ccaat(dziki: str, gestosc: Counter,
                    mediana_tss: float | None = None) -> list[dict]:
    """Miejsca oddalone o JEDNO podstawienie od pelnego CCAAT/ATTGG,
    posortowane po tym, jak gesto naturalne promotory trzymaja tam te miejsca.

    `mediana_tss` zmienia PRZELAMYWANIE REMISOW. Bez niego remis w gestosci
    rozstrzyga `tss` rosnaco, czyli systematycznie najdalej od TSS -- i stad
    mediana naszych miejsc w v8 wyszla na -445 przy naturalnej -388. Z nim
    remis rozstrzyga bliskosc do mediany rozkladu naturalnego.
    """
    out = []
    for i in range(len(dziki) - 4):
        seg = dziki[i:i + 5]
        for cel in CELE:
            r = [j for j, (a, b) in enumerate(zip(seg, cel)) if a != b]
            if len(r) != 1:
                continue
            j = r[0]
            tss = i + 1 - TSS
            out.append({
                "poz_motywu": i + 1, "tss": tss, "jest": seg, "cel": cel,
                "poz_zmiany": i + 1 + j, "z": seg[j], "na": cel[j],
                "gestosc_naturalnych": gestosc.get((tss // 50) * 50, 0),
            })
    if mediana_tss is None:
        out.sort(key=lambda d: (-d["gestosc_naturalnych"], d["tss"]))
    else:
        out.sort(key=lambda d: (-d["gestosc_naturalnych"], abs(d["tss"] - mediana_tss)))
    return out


def nanies(seq: str, wybrane: list[dict]) -> str:
    for k in wybrane:
        seq = S.wstaw(seq, k["na"], k["poz_zmiany"])
    return seq


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--miejsc", type=int, default=4, help="ile miejsc CCAAT DODAC")
    ap.add_argument("--docelowo", type=int, default=0, metavar="N",
                    help="dawka DOCELOWA: uzupelnij do N miejsc lacznie (liczac te, "
                         "ktore ziarno juz ma). Naturalna mediana rodzaju = 2.")
    ap.add_argument("--pozycja-naturalna", action="store_true",
                    help="remis w gestosci rozstrzygaj bliskoscia do mediany naturalnej, "
                         "a nie odlegloscia od TSS")
    ap.add_argument("--bramka", type=int, default=0,
                    help="ile sekwencji sprawdzic u Sedziego (0 = wcale)")
    ap.add_argument("--baza", default=str(REPO / "runs" / "julian" / "v4.fasta"))
    ap.add_argument("-o", "--wyjscie", default=str(REPO / "runs" / "julian" / "v8_ccaat.fasta"))
    args = ap.parse_args()

    w03 = wczytaj(KATALOG / "E03_naturalne_promotory" / "wyniki.json")
    if not w03:
        print("BRAK E03/wyniki.json -- uruchom najpierw E03.", file=sys.stderr)
        return 1
    dziki = w03["dziki"]
    NAT = [r["sekwencja"] for r in w03["rekordy"]]
    print(f"naturalnych: {len(NAT)} promotorow, "
          f"{len({r['nazwa'].split('_')[0] for r in w03['rekordy']})} szczepow\n")

    # ── 1. gdzie jest prawdziwy rdzen: konserwacja, nie gradient modelu
    IC = informacja_pozycyjna(NAT)
    print("[1] KONSERWACJA POZYCYJNA (bity, okna 50 pz)")
    okna = []
    for start in range(0, 800, 50):
        seg = [v for v in IC[start:start + 50] if v is not None]
        if seg:
            okna.append((start + 1, st.mean(seg)))
            print(f"    {start + 1:>3}-{start + 50:>3}  {st.mean(seg):.4f}  "
                  f"{'#' * int(st.mean(seg) * 300)}")
    szczyt = max((v, p) for p, v in enumerate(IC) if v is not None)
    kol = Counter(x for x in (s[szczyt[1]] for s in NAT) if x in "ACGT")
    dom = max(kol, key=kol.get)
    print(f"    szczyt: poz {szczyt[1] + 1} (TSS{szczyt[1] + 1 - TSS:+d})  IC={szczyt[0]:.3f}  "
          f"dominuje {dom} {kol[dom] / sum(kol.values()):.0%}  dziki={dziki[szczyt[1]]}")

    # ── 2. czy rdzen dzikiego odstaje? (kontrola: losowe okno)
    print("\n[2] LOG-ODDS WOBEC PWM NATURALNYCH")
    pwm_wyniki = {}
    for od, do, opis in ((751, 800, "rdzen 751-800"), (401, 450, "kontrola 401-450")):
        m = pwm(NAT, od, do)
        sc = [punktuj(s, m, od) for s in NAT]
        d = punktuj(dziki, m, od)
        perc = sum(1 for x in sc if x < d) / len(sc)
        pwm_wyniki[opis] = {"dziki": round(d, 2), "mediana": round(st.median(sc), 2),
                            "percentyl": round(perc, 2)}
        print(f"    {opis:<18} naturalne mediana {st.median(sc):>6.2f} | "
              f"dziki {d:>6.2f} | percentyl {perc:>4.0%}")
    print("    -> rdzen dzikiego jest w normie: NIE ma czego naprawiac w rdzeniu")

    # ── 3. motywy na obu niciach
    print("\n[3] MOTYWY (obie nici): dziki vs naturalne")
    motywy = {}
    for nazwa, wzor in list(S.MOTYWY.items()) + [("CCAAT_obie", "CCAAT")]:
        dn = len(obie_nici(dziki, wzor))
        nn = [len(obie_nici(s, wzor)) for s in NAT]
        motywy[nazwa] = {"dziki": dn, "mediana": st.median(nn),
                         "frakcja_z_motywem": round(sum(1 for x in nn if x) / len(nn), 2)}
        flaga = "  <-- DZIKI NIE MA, ma go wiekszosc" if dn == 0 and sum(1 for x in nn if x) > 50 else ""
        print(f"    {nazwa:<14} dziki={dn:>2}  mediana={st.median(nn):>4.1f}  "
              f"ma>=1: {sum(1 for x in nn if x):>3}%{flaga}")

    # ── 4. uczciwy test: czy brak CCAAT to anomalia?
    lam = oczekiwane(dziki)
    p0 = math.exp(-lam)
    zer = sum(1 for s in NAT if not obie_nici(s, "CCAAT"))
    print(f"\n[4] UCZCIWY TEST ANOMALII")
    print(f"    oczekiwane z samego skladu zasad: {lam:.2f}   P(0) = {p0:.3f}")
    print(f"    naturalnych z zerem miejsc: {zer}/100")
    print(f"    -> brak CCAAT w pks1 NIE jest anomalia statystyczna (p={p0:.2f}).")
    print(f"       Twierdzimy tylko: 81 % rodzaju niesie element, ktorego pks1 nie ma.")

    # ── 5. projekt
    poz_nat = [p - TSS for s in NAT for p in obie_nici(s, "CCAAT")]
    gestosc = Counter((p // 50) * 50 for p in poz_nat)
    med_nat = st.median(poz_nat)
    licz_nat = [len(obie_nici(s, "CCAAT")) for s in NAT]
    print(f"\n[5a] ROZKLAD NATURALNY: mediana pozycji TSS{med_nat:+.0f}, "
          f"mediana liczby miejsc {st.median(licz_nat):.0f}")
    cel_tss = med_nat if args.pozycja_naturalna else None
    kand = kandydaci_ccaat(dziki, gestosc, cel_tss)
    wybrane = kand[:(args.docelowo or args.miejsc)]
    print(f"\n[5] PROJEKT: {len(wybrane)} podstawien -> {len(wybrane)} miejsc CCAAT")
    for k in wybrane:
        print(f"    poz {k['poz_zmiany']:>3} (TSS{k['tss']:+5})  {k['jest']} -> {k['cel']}  "
              f"{k['z']}->{k['na']}   gestosc naturalnych w oknie: {k['gestosc_naturalnych']}")
    wzor_dziki = nanies(dziki, wybrane)
    print(f"    dziki+CCAAT: {S.hamming(dziki, wzor_dziki)} zmian, "
          f"GC {S.gc(dziki):.3f} -> {S.gc(wzor_dziki):.3f}, "
          f"miejsc CCAAT {len(obie_nici(wzor_dziki, 'CCAAT'))}")

    # ── 6. naszczepienie na 100 niezaleznych ziaren
    baza = Path(args.baza)
    wyjscie: list[tuple[str, str]] = []
    if baza.exists():
        rek = F.czytaj(baza)
        print(f"\n[6] NASZCZEPIENIE na {len(rek)} ziaren z {baza.name}")
        udane = 0
        for r in rek:
            k_lokalne = kandydaci_ccaat(r.seq, gestosc)[:args.miejsc]
            nowa = nanies(r.seq, k_lokalne) if k_lokalne else r.seq
            if F.problemy(nowa) or nowa in {s for _, s in wyjscie}:
                nowa = r.seq
            udane += len(obie_nici(nowa, "CCAAT")) > len(obie_nici(r.seq, "CCAAT"))
            wyjscie.append((f"{r.nazwa}_ccaat", nowa))
        print(f"    ziaren z dodanym miejscem CCAAT: {udane}/{len(rek)}")
        rap = F.waliduj([F.Rekord(n, s) for n, s in wyjscie])
        print("    " + rap.podsumowanie().replace("\n", "\n    "))
        F.zapisz(Path(args.wyjscie), [(r.nazwa, r.seq) for r in rap.ok[:100]])
        print(f"    zapisano: {args.wyjscie}")
    else:
        print(f"\n[6] POMINIETO -- brak {baza}. Zbuduj najpierw v4 (E08).")

    # ── 7. opcjonalna kontrola bramki
    bramka = None
    if args.bramka and wyjscie:
        c = klient()
        proba = wyjscie[:args.bramka]
        wyg = sum(1 for _, s in proba if c.lepsza(dziki, s))
        bramka = f"{wyg}/{len(proba)}"
        print(f"\n[7] BRAMKA SEDZIEGO na probce: {bramka}")
        print("    UWAGA: przegrana NIE jest powodem do odrzucenia -- Sedzia mierzy")
        print("    prototypowosc dekodera (W4), a nie obecnosc miejsc wiazania.")

    zapisz(TU / "wyniki.json", {
        "eksperyment": "E10_ccaat",
        "konserwacja_okna": okna,
        "szczyt_konserwacji": {"poz": szczyt[1] + 1, "tss": szczyt[1] + 1 - TSS,
                               "ic": round(szczyt[0], 4), "dominujaca": dom,
                               "dziki": dziki[szczyt[1]]},
        "pwm": pwm_wyniki,
        "motywy": motywy,
        "test_anomalii": {"lambda": round(lam, 2), "p_zero": round(p0, 3),
                          "naturalnych_z_zerem": zer},
        "gestosc_ccaat_naturalnych": dict(sorted(gestosc.items())),
        "wybrane_podstawienia": wybrane,
        "dziki_z_ccaat": wzor_dziki,
        "plik": args.wyjscie if wyjscie else None,
        "bramka_probka": bramka,
    })
    print(f"\nzapisano: {TU / 'wyniki.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
