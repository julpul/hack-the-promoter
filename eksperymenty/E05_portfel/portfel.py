#!/usr/bin/env python3
"""E05 -- budowa portfela 100 sekwencji z dwunastu niezaleznych hipotez.

Patrz PLAN.md. Zasada: TOP10 to statystyka pozycyjna, wiec liczy sie liczba
NIEZALEZNYCH hipotez, nie liczba sekwencji. Dwanascie blokow po ~8 bije piec
blokow po ~20, bo skorelowane warianty to jedno losowanie z ogona.

Bloki, ktore zaleza od nieuruchomionych eksperymentow, kurcza sie automatycznie,
a ich budzet idzie do bloku 1 (bezpieczna srednia) i 12 (ogon).

    python eksperymenty/E05_portfel/portfel.py -o runs/julian/v2.fasta
    python eksperymenty/E05_portfel/portfel.py --plan     # tylko pokaz budzet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eksperymenty.wspolne import (  # noqa: E402
    KATALOG, REPO, klient, kandydaci as K, metryki as M, wczytaj,
)
from hyppe import fasta as F, seq as S  # noqa: E402

TU = Path(__file__).resolve().parent
CEL = 100

# ilosci docelowe; bloki zalezne kurcza sie, gdy brak danych
BUDZET = {
    "01_trzon_hybryda":      12,
    "02_gatunek_punkt":       8,
    "03_gatunek_okolica":     8,
    "04_e04_najlepsza":      10,
    "05_e04_kolejne":         8,
    "06_crea":                8,
    "07_rdzen_skan":          8,
    "08_tata_skan":           8,
    "09_chimery":             8,
    "10_naturalne":           6,
    "11_dekoder_daleko":      8,
    "12_odloty":              8,
}
ELASTYCZNE = ["01_trzon_hybryda", "12_odloty"]   # tu trafia budzet z pustych blokow


def _wyn(nazwa: str) -> dict | None:
    return wczytaj(KATALOG / nazwa / "wyniki.json")


def _scorer(rekord_metryk: dict) -> float:
    """Nizej = lepiej. Uzywane tylko do sortowania wewnatrz blokow.

    Klucz glowny: zmian_pod_gatunek (niedopasowanie do P1, os niewidoczna dla
    Sedziego). Klucz pomocniczy: blad_odtworzenia (odleglosc od rozmaitosci).
    Jesli E01 orzeklo, ze te pola nie wariuja, sortowanie jest bezszkodliwe --
    po prostu nic nie zmienia.
    """
    g = rekord_metryk.get("zmian_pod_gatunek")
    b = rekord_metryk.get("blad_odtworzenia")
    return (g if isinstance(g, (int, float)) else 99) * 1000 + (
        b if isinstance(b, (int, float)) else 999)


# ── bloki ──────────────────────────────────────────────────────────────────

def blok_01(c, dziki, n, ctx):
    pula = K.wczytaj_pule()
    return {f"b01_trzon_{i:02d}": s for i, s in enumerate(list(pula.values())[:n])}


def blok_02(c, dziki, n, ctx):
    """Punkt staly kanalu gatunku (W7) + warianty czesciowe po drodze."""
    out, biezaca = {}, dziki
    for krok in range(1, 4):
        nowa = c.zastosuj_rekomendacje(biezaca)
        if nowa == biezaca:
            break
        biezaca = nowa
        out[f"b02_gatunek_it{krok}"] = biezaca
    ctx["gatunek_punkt_staly"] = biezaca
    # dopelniamy czesciowymi: pojedyncze rekomendacje naniesione osobno
    m = c.mapa(dziki)
    rek = [(p["poz"], p["zmien_na"]) for p in m["pozycje"] if p["zmien_na"] != "."]
    for poz, zas in rek:
        if len(out) >= n:
            break
        out[f"b02_gatunek_poj{poz}"] = S.wstaw(dziki, zas, poz)
    return out


def blok_03(c, dziki, n, ctx):
    """Okolica punktu stalego -- mutacje TYLKO na pozycjach swobodnych.

    Losowe mutacje nie dzialaja (W5), ale tu nie chodzi o poprawe, tylko
    o rozproszenie wokol wariantu, ktory ma uzasadnienie. Pozycje swobodne
    (rekon=0) to te, ktorych dekoder nie odtwarza -- edycja tam sie utrzyma.
    """
    baza = ctx.get("gatunek_punkt_staly", dziki)
    m = c.mapa(baza)
    swobodne = [p["poz"] for p in m["pozycje"] if p["rekon"] == 0]
    return {f"b03_okolica_{i:02d}": S.mutuj(baza, ile=3 + i, pozycje=swobodne, ziarno=i)
            for i in range(n)}


def blok_04(c, dziki, n, ctx):
    w = _wyn("E04_blok_kombinacyjny")
    if not w:
        return {}
    kom = sorted(w["komorki"], key=lambda k: _scorer(k.get("metryki", {})))
    najlepsza = kom[0]
    out = {f"b04_{najlepsza['etykieta']}": najlepsza["sekwencja"]}
    # repliki tej samej komorki + drobne wariacje na pozycjach swobodnych
    sygn = (najlepsza["A_gatunek"], najlepsza["B_crea"],
            najlepsza["C_rdzen"], najlepsza["D_tlo"])
    for k in kom[1:]:
        if len(out) >= n:
            break
        if (k["A_gatunek"], k["B_crea"], k["C_rdzen"], k["D_tlo"]) == sygn:
            out[f"b04_{k['etykieta']}"] = k["sekwencja"]
    i = 0
    while len(out) < n:
        out[f"b04_war_{i:02d}"] = S.mutuj(najlepsza["sekwencja"], ile=2, ziarno=500 + i)
        i += 1
    return out


def blok_05(c, dziki, n, ctx):
    w = _wyn("E04_blok_kombinacyjny")
    if not w:
        return {}
    kom = sorted(w["komorki"], key=lambda k: _scorer(k.get("metryki", {})))
    sygn0 = (kom[0]["A_gatunek"], kom[0]["B_crea"], kom[0]["C_rdzen"], kom[0]["D_tlo"])
    inne = [k for k in kom
            if (k["A_gatunek"], k["B_crea"], k["C_rdzen"], k["D_tlo"]) != sygn0]
    return {f"b05_{k['etykieta']}": k["sekwencja"] for k in inne[:n]}


def blok_06(c, dziki, n, ctx):
    """CreA rozbite: 4 podstawienia x 2 tla (dziki, punkt staly gatunku)."""
    from eksperymenty.E04_blok_kombinacyjny.run import rozbij_crea
    tla = [("dz", dziki), ("gat", ctx.get("gatunek_punkt_staly", dziki))]
    out = {}
    for nazwa_tla, tlo in tla:
        for z in range(4):
            if len(out) >= n:
                break
            out[f"b06_crea_{nazwa_tla}_{z}"] = rozbij_crea(tlo, ziarno=z)
    return out


def blok_07(c, dziki, n, ctx):
    """Rdzen z konsensusu E03, skan pozycji wstawienia."""
    w03 = _wyn("E03_naturalne_promotory")
    if not w03:
        return {}
    kons = w03["konsensus"]["rdzen"]["konsensus"]
    baza = ctx.get("gatunek_punkt_staly", dziki)
    out = {}
    # skan: przesuwamy okno wstawienia, zamiast dosypywac szum
    for i, start in enumerate(range(M.RDZEN_OD - 6, M.RDZEN_OD + 3, 3)):
        for tlo_n, tlo in (("dz", dziki), ("gat", baza)):
            if len(out) >= n:
                break
            koniec = start + len(kons) - 1
            if koniec > 800:
                continue
            out[f"b07_rdzen_{tlo_n}_{start}"] = K.podmien_okno(tlo, start, koniec, kons)
    return out


def blok_08(c, dziki, n, ctx):
    """TATAAA w oknie -80..-30 (poz. 720-770) -- skan co 6 pz.

    W dzikim brak kanonicznego TATA w tym oknie (H1 + skan motywow), a jest
    TATAAA na 343 (za daleko) i TATATA na 701/703 (slabszy wariant).
    """
    baza = ctx.get("gatunek_punkt_staly", dziki)
    out = {}
    for poz in range(720, 771, 6):
        if len(out) >= n:
            break
        tlo = baza if len(out) % 2 else dziki
        out[f"b08_tata_{poz}"] = S.wstaw(tlo, "TATAAA", poz)
    return out


def blok_09(c, dziki, n, ctx):
    w03 = _wyn("E03_naturalne_promotory")
    if not w03 or not w03.get("chimery"):
        return {}
    ch = sorted(w03["chimery"], key=lambda x: -int(x["bije_dzikiego"]))
    return {f"b09_{x['etykieta']}": x["sekwencja"] for x in ch[:n]}


def blok_10(c, dziki, n, ctx):
    w03 = _wyn("E03_naturalne_promotory")
    if not w03:
        return {}
    rek = w03["rekordy"]
    wygrane = [r for r in rek if r["bije_dzikiego"]]
    wybor = wygrane or sorted(rek, key=lambda r: _scorer(r.get("metryki", {})))
    return {f"b10_nat_{r['nazwa'][:20]}": r["sekwencja"] for r in wybor[:n]}


def blok_11(c, dziki, n, ctx):
    """Maksymalny dystans osiagalny w latencie: poziom 0, ile_kodow 16."""
    odp = c.edycje(dziki, poziom=0, ile_kodow=16, opcji=n, ziarno=999)
    return {f"b11_dekoder_{o['nr']}": o["sekwencja"] for o in odp["opcje"][:n]}


def blok_12(c, dziki, n, ctx):
    """Odloty + dwie sondy diagnostyczne (patrz PLAN.md)."""
    out = {}
    baza = ctx.get("gatunek_punkt_staly", dziki)

    # SONDA GOODHARTA: przesycone TATA. Sekcja 6 briefu wprost o to prosi.
    s = dziki
    for poz in range(700, 780, 8):
        s = S.wstaw(s, "TATAAA", poz)
    out["b12_sonda_goodhart_tata"] = s

    # SONDA N: 80 znakow N (dokladnie prog 10%) w pozycjach o niskim gradiencie.
    m = c.mapa(dziki)
    niskie = [p["poz"] for p in m["pozycje"] if p["wagaP"] < 0.05][:80]
    lista = list(dziki)
    for p in niskie:
        lista[p - 1] = "N"
    out["b12_sonda_N80"] = "".join(lista)

    # wszystko naraz: gatunek + CreA + rdzen + TATA
    try:
        from eksperymenty.E04_blok_kombinacyjny.run import rdzen_z_e03, rozbij_crea
        s = rozbij_crea(baza)
        s = S.wstaw(s, "TATAAA", 742)
        s = K.podmien_okno(s, M.RDZEN_OD, M.RDZEN_DO, rdzen_z_e03()[0])
        out["b12_wszystko_naraz"] = s
    except Exception as e:  # noqa: BLE001
        print(f"  [b12 wszystko_naraz pominiete] {e}", file=sys.stderr)

    # dalekie odloty z latentu
    i = 0
    while len(out) < n:
        odp = c.edycje(baza, poziom=0, ile_kodow=16, opcji=4, ziarno=1300 + i)
        for o in odp["opcje"]:
            if len(out) >= n:
                break
            out[f"b12_odlot_{i}_{o['nr']}"] = o["sekwencja"]
        i += 1
    return out


BLOKI = {
    "01_trzon_hybryda": blok_01, "02_gatunek_punkt": blok_02,
    "03_gatunek_okolica": blok_03, "04_e04_najlepsza": blok_04,
    "05_e04_kolejne": blok_05, "06_crea": blok_06,
    "07_rdzen_skan": blok_07, "08_tata_skan": blok_08,
    "09_chimery": blok_09, "10_naturalne": blok_10,
    "11_dekoder_daleko": blok_11, "12_odloty": blok_12,
}


# ── skladanie ──────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--wyjscie", default=str(REPO / "runs" / "julian" / "v2.fasta"))
    ap.add_argument("--plan", action="store_true", help="tylko budzet, bez wywolan API")
    args = ap.parse_args()

    dostepne = {n: (_wyn(k) is not None) for n, k in (
        ("04_e04_najlepsza", "E04_blok_kombinacyjny"),
        ("05_e04_kolejne", "E04_blok_kombinacyjny"),
        ("07_rdzen_skan", "E03_naturalne_promotory"),
        ("09_chimery", "E03_naturalne_promotory"),
        ("10_naturalne", "E03_naturalne_promotory"),
    )}
    print("zaleznosci:")
    for n, ok in dostepne.items():
        print(f"  {n:<22} {'OK' if ok else 'BRAK -- blok pominiety'}")

    if args.plan:
        for n, ile in BUDZET.items():
            print(f"  {n:<22} {ile:>3}" + ("" if dostepne.get(n, True) else "  -> 0"))
        return 0

    c = klient()
    dziki = c.dziki_seq()
    ctx: dict = {}
    zebrane: dict[str, str] = {}
    widziane: set[str] = set()          # dedup po SEKWENCJI, nie po etykiecie

    def przyjmij(etyk: str, sekw: str) -> bool:
        if sekw in widziane or etyk in zebrane or F.problemy(sekw):
            return False
        zebrane[etyk] = sekw
        widziane.add(sekw)
        return True

    for nazwa, ile in BUDZET.items():
        try:
            wynik = BLOKI[nazwa](c, dziki, ile, ctx)
        except Exception as e:  # noqa: BLE001
            print(f"  [{nazwa}] BLAD: {e}", file=sys.stderr)
            wynik = {}
        dodano = 0
        for k, v in wynik.items():
            if dodano >= ile:
                break
            dodano += przyjmij(k, v)
        print(f"  {nazwa:<22} plan {ile:>3}  zbudowano {dodano:>3}"
              + ("" if dodano == ile else "   <- niedobor, budzet idzie do dopelnienia"))

    # ── dopelnienie: rozprowadzamy niedobor po TANICH SKANACH, nie w jedno miejsce.
    # Skan parametru jest jednoczesnie bardziej rozny i bardziej informatywny
    # niz szum wokol jednego punktu (patrz PLAN.md, W11).
    brak = CEL - len(zebrane)
    if brak:
        print(f"\ndopelnienie: brakuje {brak} -> rozprowadzam po skanach parametrow")
        baza = ctx.get("gatunek_punkt_staly", dziki)
        m = c.mapa(baza)
        swobodne = [p["poz"] for p in m["pozycje"] if p["rekon"] == 0]
        for i in range(2000):
            if len(zebrane) >= CEL:
                break
            tryb = i % 4
            if tryb == 0:      # skan TATA co 2 pz w oknie -80..-30
                poz = 720 + (i // 4) % 50
                przyjmij(f"dop_tata_{poz}_{i}", S.wstaw(baza if i % 8 < 4 else dziki,
                                                        "TATAAA", poz))
            elif tryb == 1:    # okolica punktu stalego, tylko pozycje swobodne
                przyjmij(f"dop_okolica_{i}",
                         S.mutuj(baza, ile=2 + (i // 4) % 6, pozycje=swobodne, ziarno=i))
            elif tryb == 2:    # krzyzowanie trzonu z wariantem gatunkowym
                pula = list(zebrane.values())
                przyjmij(f"dop_krzyz_{i}",
                         S.krzyzuj(pula[i % len(pula)], baza, punktow=2, ziarno=i))
            else:              # skan okna rdzenia poli-pirymidynowego
                poz = M.RDZEN_OD - 4 + (i // 4) % 5
                przyjmij(f"dop_rdzen_{poz}_{i}",
                         K.podmien_okno(dziki, poz, poz + 5, "CTCTCT"))

    rekordy = [F.Rekord(k, v) for k, v in list(zebrane.items())[:CEL]]
    rap = F.waliduj(rekordy)
    print("\n" + rap.podsumowanie())

    p = Path(args.wyjscie)
    F.zapisz(p, [(r.nazwa, r.seq) for r in rap.ok[:CEL]])
    print(f"\nzapisano: {p}  ({len(rap.ok[:CEL])} sekwencji)")
    print("\nnastepnie:")
    print(f"  python -m hyppe waliduj {p}")
    print(f"  python -m hyppe wgraj {p} --dry-run")
    print(f"  python -m hyppe wgraj {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
