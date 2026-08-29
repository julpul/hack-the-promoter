"""Testy operacji na sekwencjach -- kluczowe: nic nie moze zepsuc 800 pz."""

import random
import unittest

from hyppe import fasta as F
from hyppe import seq as S

BAZA = ("ACGTTGCAAGGCCTTAAGCT" * 40)  # 800 pz


class TestNiezmiennikDlugosci(unittest.TestCase):
    def test_baza_jest_poprawna(self):
        self.assertEqual(len(BAZA), 800)
        self.assertEqual(F.problemy(BAZA), [])

    def test_mutuj_zachowuje_dlugosc_i_alfabet(self):
        for ziarno in range(20):
            s = S.mutuj(BAZA, ile=50, ziarno=ziarno)
            self.assertEqual(F.problemy(s), [], f"ziarno {ziarno}")

    def test_krzyzuj_zachowuje_dlugosc(self):
        b = S.mutuj(BAZA, ile=200, ziarno=1)
        for punktow in (1, 2, 3, 5):
            self.assertEqual(len(S.krzyzuj(BAZA, b, punktow=punktow, ziarno=punktow)), 800)

    def test_wstaw_zachowuje_dlugosc(self):
        s = S.wstaw(BAZA, "TATAAA", 100)
        self.assertEqual(len(s), 800)
        self.assertEqual(s[99:105], "TATAAA")

    def test_wstaw_poza_zakresem_rzuca(self):
        with self.assertRaises(ValueError):
            S.wstaw(BAZA, "TATAAA", 799)


class TestMutuj(unittest.TestCase):
    def test_liczba_zmian_zgadza_sie(self):
        s = S.mutuj(BAZA, ile=13, ziarno=3)
        self.assertEqual(S.hamming(BAZA, s), 13)

    def test_mutacja_zawsze_zmienia_zasade(self):
        s = S.mutuj(BAZA, ile=800, ziarno=5)
        self.assertEqual(S.hamming(BAZA, s), 800)

    def test_ogranicza_sie_do_podanych_pozycji(self):
        pozycje = [10, 20, 30, 40]
        s = S.mutuj(BAZA, ile=4, pozycje=pozycje, ziarno=2)
        zmienione = {p for p, _, _ in S.rozne_pozycje(BAZA, s)}
        self.assertTrue(zmienione <= set(pozycje))

    def test_deterministyczna_przy_tym_samym_ziarnie(self):
        self.assertEqual(S.mutuj(BAZA, ile=20, ziarno=42), S.mutuj(BAZA, ile=20, ziarno=42))

    def test_rng_wspoldzielony(self):
        r = random.Random(1)
        a = S.mutuj(BAZA, ile=5, rng=r)
        b = S.mutuj(BAZA, ile=5, rng=r)
        self.assertNotEqual(a, b)

    def test_pusta_lista_pozycji_nie_zmienia(self):
        self.assertEqual(S.mutuj(BAZA, ile=5, pozycje=[]), BAZA)


class TestPomocnicze(unittest.TestCase):
    def test_rewers_komplement(self):
        self.assertEqual(S.rewers_komplement("ACGTN"), "NACGT")
        self.assertEqual(S.rewers_komplement(S.rewers_komplement(BAZA)), BAZA)

    def test_gc(self):
        self.assertAlmostEqual(S.gc("GGCC"), 1.0)
        self.assertAlmostEqual(S.gc("AATT"), 0.0)
        self.assertAlmostEqual(S.gc("ACGT"), 0.5)

    def test_gc_ignoruje_N(self):
        self.assertAlmostEqual(S.gc("GCNN"), 1.0)

    def test_gc_pustej(self):
        self.assertEqual(S.gc("NNN"), 0.0)

    def test_rozne_pozycje_sa_1_based(self):
        self.assertEqual(S.rozne_pozycje("AC", "TC"), [(1, "A", "T")])

    def test_znajdz(self):
        self.assertEqual(S.znajdz("AATATAAAGG", "TATAAA"), [3])

    def test_znajdz_iupac(self):
        # SYGGRG: S=[GC] Y=[CT] G G R=[AG] G
        self.assertEqual(S.znajdz_iupac("AAGCGGAGTT", "SYGGRG"), [3])

    def test_skanuj_motywy_zwraca_wszystkie_klucze(self):
        wynik = S.skanuj_motywy(BAZA)
        self.assertEqual(set(wynik), set(S.MOTYWY))


if __name__ == "__main__":
    unittest.main()
