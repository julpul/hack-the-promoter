"""Testy filtrow zgodnych z regulaminem: 800 pz, ACGTN, <=10% N, unikalnosc."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from hyppe import fasta as F


def seq(n=800, litera="A"):
    return litera * n


class TestProblemy(unittest.TestCase):
    def test_poprawna_przechodzi(self):
        self.assertEqual(F.problemy("ACGT" * 200), [])

    def test_zla_dlugosc(self):
        for n in (799, 801, 0, 1600):
            with self.subTest(n=n):
                self.assertTrue(any("dlugosc" in p for p in F.problemy(seq(n))))

    def test_znaki_spoza_alfabetu(self):
        s = "U" + seq(799)
        self.assertTrue(any("spoza ACGTN" in p for p in F.problemy(s)))

    def test_male_litery_sa_ok_po_walidacji(self):
        # problemy() dostaje surowy tekst, ale waliduj() normalizuje do wielkich
        rek = [F.Rekord("m", "acgt" * 200)]
        raport = F.waliduj(rek)
        self.assertEqual(len(raport.ok), 1)
        self.assertEqual(raport.ok[0].seq, "ACGT" * 200)

    # --- prog N: 10% z 800 = 80 ---

    def test_n_dokladnie_10_procent_przechodzi(self):
        s = "N" * 80 + "A" * 720
        self.assertEqual(len(s), 800)
        self.assertEqual(F.problemy(s), [], "80 N to dokladnie 10%, ma przejsc")

    def test_n_81_odrzucone(self):
        s = "N" * 81 + "A" * 719
        bledy = F.problemy(s)
        self.assertTrue(any("N =" in b for b in bledy), bledy)

    def test_n_79_przechodzi(self):
        self.assertEqual(F.problemy("N" * 79 + "A" * 721), [])

    def test_prog_liczony_po_normalizacji(self):
        raport = F.waliduj([F.Rekord("n", "n" * 81 + "a" * 719)])
        self.assertEqual(len(raport.ok), 0)
        self.assertEqual(len(raport.odrzucone), 1)


class TestWaliduj(unittest.TestCase):
    def test_duplikaty_zostawiaja_pierwsze_wystapienie(self):
        s = "ACGT" * 200
        raport = F.waliduj([F.Rekord("a", s), F.Rekord("b", s), F.Rekord("c", "TGCA" * 200)])
        self.assertEqual([r.nazwa for r in raport.ok], ["a", "c"])
        self.assertEqual(raport.duplikaty, ["b"])

    def test_duplikat_niezalezny_od_wielkosci_liter(self):
        raport = F.waliduj([F.Rekord("a", "acgt" * 200), F.Rekord("b", "ACGT" * 200)])
        self.assertEqual(len(raport.ok), 1)

    def test_raport_liczy_ocenionych_max_100(self):
        rekordy = [F.Rekord(f"s{i}", "A" * i + "C" * (800 - i)) for i in range(1, 130)]
        raport = F.waliduj(rekordy)
        self.assertEqual(len(raport.ok), 129)
        self.assertEqual(raport.ocenionych, 100)

    def test_ostrzezenie_gdy_mniej_niz_100(self):
        raport = F.waliduj([F.Rekord("a", "ACGT" * 200)])
        self.assertIn("brakuje 99", raport.podsumowanie())

    def test_odrzucone_maja_powod(self):
        raport = F.waliduj([F.Rekord("krotka", "ACGT")])
        self.assertEqual(len(raport.odrzucone), 1)
        self.assertIn("dlugosc 4", raport.odrzucone[0][1])


class TestIO(unittest.TestCase):
    def test_round_trip(self):
        rekordy = [F.Rekord("a", "ACGT" * 200), F.Rekord("b", "TTTT" * 200)]
        with TemporaryDirectory() as d:
            p = Path(d) / "x.fasta"
            F.zapisz(p, rekordy)
            wczytane = F.czytaj(p)
        self.assertEqual([(r.nazwa, r.seq) for r in wczytane],
                         [(r.nazwa, r.seq) for r in rekordy])

    def test_czyta_sekwencje_lamane_na_wiele_linii(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "wrap.fasta"
            p.write_text(">x\n" + "\n".join("ACGT" * 20 for _ in range(10)) + "\n")
            rek = F.czytaj(p)
        self.assertEqual(len(rek), 1)
        self.assertEqual(len(rek[0].seq), 800)

    def test_na_tekst_akceptuje_krotki(self):
        tekst = F.na_tekst([("a", "ACGT")])
        self.assertEqual(tekst, ">a\nACGT")

    def test_zapisz_tworzy_katalogi(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "gleboko" / "tu" / "x.fasta"
            F.zapisz(p, [("a", "ACGT")])
            self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
