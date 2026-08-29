"""CLI: python -m hyppe <komenda> [flagi]  (albo ./hyppe.py po chmod +x)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import fasta as F
from . import seq as S
from . import strategie
from .client import ApiError, Client
from .config import REPO_ROOT

RUNS = REPO_ROOT / "runs"


def _klient(a) -> Client:
    return Client.from_env(api_key=a.api_key, url=a.url)


def _wypisz(obj, jako_json: bool) -> None:
    if jako_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))


def _wczytaj_seq(arg: str, c: Client | None = None) -> str:
    """Argument sekwencji: 'dziki', sciezka do pliku (FASTA lub goly tekst) albo sama sekwencja."""
    if arg == "dziki":
        assert c is not None
        return c.dziki_seq()
    p = Path(arg)
    if p.exists():
        rek = F.czytaj(p)
        if rek:
            return rek[0].seq
        return "".join(p.read_text().split())
    return arg.strip().upper()


# ---------------- komendy ----------------


def cmd_me(a):
    j = _klient(a).me()
    if a.json:
        return _wypisz(j, True)
    print("druzyna    :", j.get("druzyna"), "|", j.get("uczestnik"))
    print("klucz wazny:", j.get("wazny_do"))
    print("limity/min :", j.get("limity_na_minute"))
    print("wgranie za :", j.get("zgloszenie_mozliwe_za_s"), "s")


def cmd_dziki(a):
    c = _klient(a)
    d = c.dziki()
    if a.json:
        return _wypisz(d, True)
    if a.out:
        F.zapisz(a.out, [F.Rekord(d.get("nazwa", "dziki"), d["sekwencja"])])
        print(f"zapisano {a.out}")
    print(f"{d.get('nazwa')} | gen {d.get('gen')} | {d.get('genom')}")
    print(f"dlugosc {d.get('dlugosc')} bp | sha256[:12] = {d.get('sha256_12')}")
    print(f"GC = {S.gc(d['sekwencja']):.1%}")
    if not a.out:
        print(d["sekwencja"])


def cmd_mapa(a):
    c = _klient(a)
    seq = _wczytaj_seq(a.sekwencja, c)
    m = c.mapa(seq, od=a.od, ile=a.ile)
    if a.json:
        return _wypisz(m, True)
    print("gatunek      :", m.get("gatunek"))
    print("odtwarza sie : %.4f (nie odtwarza %s z 800)"
          % (m.get("rekon_frakcja", 0), m.get("nie_rekonstruuje")))
    print("zmian pod P1 :", m.get("zmian_pod_gatunek"),
          "| blad odtworzenia:", m.get("blad_odtworzenia"))
    print("warstwy      :", m.get("rozklad_warstw"))
    rek = [w for w in m["pozycje"] if w["zmien_na"] != "."]
    swobodne = [w["poz"] for w in m["pozycje"] if w["rekon"] == 0]
    nadpisze = [w["poz"] for w in m["pozycje"] if w["rekon"] == 1 and sum(w["warstwy"]) == 0]
    print(f"\nREKOMENDACJE: {len(rek)}")
    for w in rek[: a.limit]:
        print("   poz %3d: %s -> %s  (warstwy %s)" % (w["poz"], w["wej"], w["zmien_na"], w["warstwy"]))
    if len(rek) > a.limit:
        print(f"   ... i {len(rek) - a.limit} wiecej (--limit)")
    print(f"SWOBODNE {len(swobodne)}, pierwsze 15: {swobodne[:15]}")
    print(f"NADPISZE {len(nadpisze)}, pierwsze 15: {nadpisze[:15]}")
    if a.zastosuj:
        kand = c.zastosuj_rekomendacje(seq, m)
        F.zapisz(a.zastosuj, [F.Rekord("z_mapy", kand)])
        print(f"\nzapisano wariant z rekomendacjami -> {a.zastosuj} "
              f"({S.hamming(seq, kand)} zmian)")


def cmd_edycje(a):
    c = _klient(a)
    seq = _wczytaj_seq(a.sekwencja, c)
    e = c.edycje(seq, poziom=a.poziom, ile_kodow=a.ile_kodow, opcji=a.opcji, ziarno=a.ziarno)
    if a.json:
        return _wypisz(e, True)
    print("warstwa %s | slotow %s | alfabet %s | blad rekonstrukcji %s"
          % (e.get("warstwa"), e.get("slotow"), e.get("alfabet"),
             e.get("blad_rekonstrukcji_pozycji")))
    for o in e["opcje"]:
        print("  nr %-3s zmian %-5s hamming(baza) %d"
              % (o.get("nr"), o.get("zmiany"), S.hamming(seq, o["sekwencja"])))
    if a.out:
        F.zapisz(a.out, [F.Rekord(f"edy_{o['nr']}", o["sekwencja"]) for o in e["opcje"]])
        print(f"zapisano {len(e['opcje'])} wariantow -> {a.out}")


def cmd_sedzia(a):
    c = _klient(a)
    if a.plik:
        baza = _wczytaj_seq(a.baza, c)
        rekordy = F.waliduj(F.czytaj(a.plik)).ok
        wygrane = []
        for i, r in enumerate(rekordy, 1):
            wynik = c.sedzia(baza, r.seq, "baza", r.nazwa)
            zwyciezca = wynik.get("silniejsza_idx") == 1
            wygrane.append((r.nazwa, zwyciezca))
            print(f"[{i}/{len(rekordy)}] {r.nazwa:<28} {'WYGRAL' if zwyciezca else 'przegral'}")
        ile = sum(1 for _, w in wygrane if w)
        print(f"\nprzebily baze: {ile} z {len(wygrane)} ({100 * ile / max(len(wygrane), 1):.0f}%)")
        if a.out:
            wybrane = [F.Rekord(n, dict((r.nazwa, r.seq) for r in rekordy)[n])
                       for n, w in wygrane if w]
            F.zapisz(a.out, wybrane)
            print(f"zwyciezcy -> {a.out}")
        return
    a_seq = _wczytaj_seq(a.a, c)
    b_seq = _wczytaj_seq(a.b, c)
    w = c.sedzia(a_seq, b_seq, a.nazwa_a, a.nazwa_b)
    if a.json:
        return _wypisz(w, True)
    print(f"silniejsza: {w.get('silniejsza')} (idx {w.get('silniejsza_idx')})")


def cmd_pula(a):
    c = _klient(a)
    baza = _wczytaj_seq(a.baza, c)
    opcje = dict(ile=a.ile, poziom=a.poziom, ziarno=a.ziarno)
    pula = strategie.uruchom(a.strategia, c, baza, **opcje)
    rekordy = [F.Rekord(n, s) for n, s in pula.items()]
    raport = F.waliduj(rekordy)
    out = Path(a.out) if a.out else RUNS / f"pula_{a.strategia}.fasta"
    F.zapisz(out, raport.ok[: F.LIMIT_OCENIANYCH])
    print(raport.podsumowanie())
    print(f"\nzapisano {min(len(raport.ok), F.LIMIT_OCENIANYCH)} sekwencji -> {out}")


def cmd_waliduj(a):
    raport = F.waliduj(F.czytaj(a.plik))
    print(raport.podsumowanie())
    if a.fix:
        F.zapisz(a.fix, raport.ok[: F.LIMIT_OCENIANYCH])
        print(f"\nwyczyszczony plik -> {a.fix}")
    sys.exit(1 if raport.odrzucone and not a.fix else 0)


def cmd_wgraj(a):
    raport = F.waliduj(F.czytaj(a.plik))
    print(raport.podsumowanie())
    if not raport.ok:
        sys.exit("brak poprawnych sekwencji -- nic nie wysylam")
    if a.suchy:
        print("\n--dry-run: nic nie wyslano")
        return
    if len(raport.ok) < F.LIMIT_OCENIANYCH and not a.force:
        sys.exit(f"\nmniej niz {F.LIMIT_OCENIANYCH} sekwencji -> traci ALL100. "
                 "Dodaj --force jesli swiadomie.")
    c = _klient(a)
    tekst = F.na_tekst(raport.ok[: F.LIMIT_OCENIANYCH])
    try:
        r = c.wgraj(tekst)
    except ApiError as e:
        if e.kod == 429:
            sys.exit(f"429: odstep 5 min od poprzedniego wgrania. {e.tresc}")
        raise
    if a.json:
        return _wypisz(r, True)
    print("\n--- filtrowanie serwera ---")
    for k, v in (r.get("filtrowanie") or {}).items():
        print("   %-26s %s" % (k, v))
    print("--- wynik ---")
    for k in ("ocenionych", "dzielnik_top10", "dzielnik_top100",
              "pozycja_top10", "pozycja_top100", "punkty_razem"):
        print("   %-26s %s" % (k, r.get(k)))
    RUNS.mkdir(exist_ok=True)
    (RUNS / "ostatnie_wgranie.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_ranking(a):
    t = _klient(a).ranking()
    if a.json:
        return _wypisz(t, True)
    print("druzyn %s | startujacych %s | wasza pozycja: %s"
          % (t.get("n_druzyn"), t.get("n_startujacych"), t.get("twoja_pozycja")))
    print("\n%-4s %-13s %-6s %-8s %-9s %-7s %s"
          % ("poz", "druzyna", "ocen", "TOP10", "TOP100", "razem", "wgranie"))
    print("-" * 74)
    for x in t.get("ranking", []):
        print("%-4s %-13s %-6s %-8s %-9s %-7s %s"
              % (x.get("pozycja"), x.get("druzyna"), x.get("ocenionych"),
                 x.get("punkty_top10"), x.get("punkty_top100"),
                 x.get("punkty_razem"), x.get("wgranie_o") or "-"))


def cmd_analiza(a):
    c = None if a.sekwencja != "dziki" else _klient(a)
    seq = _wczytaj_seq(a.sekwencja, c)
    print(f"dlugosc {len(seq)} | GC {S.gc(seq):.1%} | sklad {S.sklad(seq)}")
    print("\nmotywy:")
    for nazwa, poz in S.skanuj_motywy(seq).items():
        print("   %-12s %d x %s" % (nazwa, len(poz), poz[:12]))
    if a.porownaj:
        inna = _wczytaj_seq(a.porownaj, _klient(a))
        roz = S.rozne_pozycje(seq, inna)
        print(f"\nroznic wobec {a.porownaj}: {len(roz)}")
        for p, x, y in roz[:40]:
            print(f"   poz {p:3d}: {x} -> {y}")


# ---------------- parser ----------------


def zbuduj_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hyppe", description="CLI do API hackathonu Hack the Promoter")
    p.add_argument("--api-key", help="nadpisuje HYPPE_API_KEY z .env")
    p.add_argument("--url", help="nadpisuje HYPPE_URL")
    p.add_argument("--json", action="store_true", help="surowa odpowiedz JSON")
    pod = p.add_subparsers(dest="cmd", required=True)

    pod.add_parser("me", help="stan klucza i limity").set_defaults(fn=cmd_me)

    d = pod.add_parser("dziki", help="pobierz promotor wyjsciowy")
    d.add_argument("-o", "--out", help="zapisz jako FASTA")
    d.set_defaults(fn=cmd_dziki)

    m = pod.add_parser("mapa", help="mapa pozycji z Nawigatora")
    m.add_argument("sekwencja", nargs="?", default="dziki",
                   help="'dziki' | sciezka do FASTA | sama sekwencja")
    m.add_argument("--od", type=int, default=0)
    m.add_argument("--ile", type=int, default=800)
    m.add_argument("--limit", type=int, default=40, help="ile rekomendacji wypisac")
    m.add_argument("--zastosuj", help="zapisz wariant z naniesionymi rekomendacjami")
    m.set_defaults(fn=cmd_mapa)

    e = pod.add_parser("edycje", help="propozycje edycji latentu")
    e.add_argument("sekwencja", nargs="?", default="dziki")
    e.add_argument("--poziom", type=int, default=2, choices=[0, 1, 2])
    e.add_argument("--ile-kodow", type=int, default=8, dest="ile_kodow")
    e.add_argument("--opcji", type=int, default=8)
    e.add_argument("--ziarno", type=int)
    e.add_argument("-o", "--out", help="zapisz warianty jako FASTA")
    e.set_defaults(fn=cmd_edycje)

    s = pod.add_parser("sedzia", help="porownanie pary albo calego pliku z baza")
    s.add_argument("a", nargs="?", default="dziki")
    s.add_argument("b", nargs="?")
    s.add_argument("--nazwa-a", default="a")
    s.add_argument("--nazwa-b", default="b")
    s.add_argument("--plik", help="FASTA: kazda sekwencja vs --baza")
    s.add_argument("--baza", default="dziki")
    s.add_argument("-o", "--out", help="zapisz zwyciezcow jako FASTA")
    s.set_defaults(fn=cmd_sedzia)

    g = pod.add_parser("pula", help="wygeneruj pule kandydatow strategia")
    g.add_argument("--strategia", default="nawigator",
                   choices=sorted(strategie.REJESTR))
    g.add_argument("--baza", default="dziki")
    g.add_argument("--ile", type=int, default=100)
    g.add_argument("--poziom", type=int, default=2)
    g.add_argument("--ziarno", type=int, default=7)
    g.add_argument("-o", "--out")
    g.set_defaults(fn=cmd_pula)

    w = pod.add_parser("waliduj", help="sprawdz FASTA lokalnie (filtry serwera)")
    w.add_argument("plik")
    w.add_argument("--fix", help="zapisz odfiltrowana wersje pod ta sciezka")
    w.set_defaults(fn=cmd_waliduj)

    u = pod.add_parser("wgraj", help="zgloszenie FASTA (raz na 5 min)")
    u.add_argument("plik")
    u.add_argument("-n", "--dry-run", dest="suchy", action="store_true")
    u.add_argument("--force", action="store_true", help="wyslij mimo <100 sekwencji")
    u.set_defaults(fn=cmd_wgraj)

    pod.add_parser("ranking", help="tablica wynikow").set_defaults(fn=cmd_ranking)

    an = pod.add_parser("analiza", help="statystyki i motywy (offline)")
    an.add_argument("sekwencja", nargs="?", default="dziki")
    an.add_argument("--porownaj", help="druga sekwencja/plik do diffa")
    an.set_defaults(fn=cmd_analiza)

    return p


def main(argv=None) -> None:
    a = zbuduj_parser().parse_args(argv)
    try:
        a.fn(a)
    except ApiError as e:
        sys.exit(str(e))
    except RuntimeError as e:
        sys.exit(str(e))
    except KeyboardInterrupt:
        sys.exit("\nprzerwano")


if __name__ == "__main__":
    main()
