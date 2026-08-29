"""Testy CLI i rejestru strategii -- bez ruchu sieciowego."""

import contextlib
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from hyppe import cli, strategie
from hyppe import fasta as F

DOBRA = "ACGT" * 200


def uruchom(argv):
    """Zwraca (stdout, kod_wyjscia). None = brak sys.exit."""
    buf = io.StringIO()
    kod = None
    try:
        with contextlib.redirect_stdout(buf):
            cli.main(argv)
    except SystemExit as e:
        kod = e.code
    return buf.getvalue(), kod


class TestParser(unittest.TestCase):
    def test_wszystkie_komendy_maja_handler(self):
        p = cli.zbuduj_parser()
        for komenda in ("me", "dziki", "mapa", "edycje", "sedzia", "pula",
                        "waliduj", "wgraj", "ranking", "analiza"):
            with self.subTest(komenda=komenda):
                a = p.parse_args([komenda] + (["x"] if komenda in ("waliduj", "wgraj") else []))
                self.assertTrue(callable(a.fn))

    def test_domyslne_wartosci_mapy(self):
        a = cli.zbuduj_parser().parse_args(["mapa"])
        self.assertEqual((a.sekwencja, a.od, a.ile), ("dziki", 0, 800))

    def test_brak_komendy_konczy_bledem(self):
        with self.assertRaises(SystemExit):
            cli.zbuduj_parser().parse_args([])


class TestWaliduj(unittest.TestCase):
    def test_czysty_plik_konczy_zerem(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "ok.fasta"
            F.zapisz(p, [(f"s{i}", "A" * i + "C" * (800 - i)) for i in range(1, 101)])
            out, kod = uruchom(["waliduj", str(p)])
        self.assertIn("do oceny        : 100", out)
        self.assertIn(kod, (0, None))

    def test_zly_plik_konczy_jedynka(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "zly.fasta"
            F.zapisz(p, [("krotka", "ACGT"), ("duzo_n", "N" * 81 + "A" * 719)])
            out, kod = uruchom(["waliduj", str(p)])
        self.assertEqual(kod, 1)
        self.assertIn("krotka", out)
        self.assertIn("duzo_n", out)

    def test_fix_zapisuje_czysta_wersje(self):
        with TemporaryDirectory() as d:
            p, fix = Path(d) / "zly.fasta", Path(d) / "czysty.fasta"
            F.zapisz(p, [("krotka", "ACGT"), ("dobra", DOBRA)])
            out, kod = uruchom(["waliduj", str(p), "--fix", str(fix)])
            wynik = F.czytaj(fix)
        self.assertIn(kod, (0, None))
        self.assertEqual([r.nazwa for r in wynik], ["dobra"])


class TestWgrajDryRun(unittest.TestCase):
    """Dry-run nie moze dotykac sieci ani wymagac klucza API."""

    def test_dry_run_nie_wysyla(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "x.fasta"
            F.zapisz(p, [(f"s{i}", "A" * i + "C" * (800 - i)) for i in range(1, 101)])
            out, kod = uruchom(["wgraj", str(p), "--dry-run"])
        self.assertIn("nic nie wyslano", out)
        self.assertIn(kod, (0, None))

    def test_blokuje_wysylke_ponizej_100_bez_force(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "malo.fasta"
            F.zapisz(p, [("a", DOBRA)])
            out, kod = uruchom(["wgraj", str(p)])
        self.assertIsInstance(kod, str)
        self.assertIn("ALL100", kod)

    def test_pusty_plik_zatrzymuje(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "pusto.fasta"
            F.zapisz(p, [("zla", "ACGT")])
            _, kod = uruchom(["wgraj", str(p)])
        self.assertIsInstance(kod, str)
        self.assertIn("brak poprawnych", kod)


class TestStrategie(unittest.TestCase):
    def test_wbudowane_sa_zarejestrowane(self):
        for nazwa in ("nawigator", "mutacje", "hybryda"):
            self.assertIn(nazwa, strategie.REJESTR)

    def test_nieznana_strategia_rzuca(self):
        with self.assertRaises(KeyError):
            strategie.uruchom("nie-ma-takiej", None, DOBRA)

    def test_duplikat_nazwy_rzuca(self):
        with self.assertRaises(KeyError):
            strategie.strategia("nawigator")(lambda *a, **k: {})

    def test_mutacje_daja_poprawne_sekwencje(self):
        class FakeClient:
            def mapa(self, seq, **kw):
                return {"pozycje": [{"poz": i, "rekon": 0, "warstwy": [0, 0, 0],
                                     "zmien_na": ".", "wej": seq[i - 1]}
                                    for i in range(1, 801)]}

        pula = strategie.uruchom("mutacje", FakeClient(), DOBRA, ile=25, ziarno=1)
        self.assertEqual(len(pula), 25)
        self.assertEqual(len(set(pula.values())), 25, "sekwencje musza byc unikalne")
        for nazwa, s in pula.items():
            self.assertEqual(F.problemy(s), [], nazwa)


if __name__ == "__main__":
    unittest.main()
