"""Testy klienta na atrapie transportu -- bez ruchu sieciowego."""

import io
import json
import unittest
import urllib.error
from unittest import mock

from hyppe.client import ApiError, Client, RateLimiter
from hyppe.config import Config

BAZA = "ACGT" * 200


def klient(**kw):
    return Client(Config(api_key="test", url="https://przyklad.test", retries=3), **kw)


class TestWarstwaWygody(unittest.TestCase):
    def setUp(self):
        self.c = klient(przestrzegaj_limitow=False)
        self.wywolania = []

    def _fake(self, odpowiedzi):
        def wolaj(sciezka, dane=None):
            self.wywolania.append((sciezka, dane))
            wynik = odpowiedzi[sciezka]
            return (200, wynik(dane) if callable(wynik) else wynik)

        return wolaj

    def test_zastosuj_rekomendacje(self):
        mapa = {"pozycje": [
            {"poz": 1, "wej": "A", "zmien_na": "T", "rekon": 1, "warstwy": [1, 0, 0]},
            {"poz": 2, "wej": "C", "zmien_na": ".", "rekon": 1, "warstwy": [0, 0, 0]},
            {"poz": 800, "wej": "T", "zmien_na": "G", "rekon": 0, "warstwy": [0, 1, 0]},
        ]}
        wynik = self.c.zastosuj_rekomendacje(BAZA, mapa)
        self.assertEqual(len(wynik), 800)
        self.assertEqual(wynik[0], "T")
        self.assertEqual(wynik[1], BAZA[1])
        self.assertEqual(wynik[799], "G")

    def test_zastosuj_rekomendacje_pobiera_mape_gdy_brak(self):
        self.c.wolaj = self._fake({"/nawigator/mapa": {"pozycje": []}})
        self.c.zastosuj_rekomendacje(BAZA)
        self.assertEqual(self.wywolania[0][0], "/nawigator/mapa")

    def test_lepsza(self):
        self.c.wolaj = self._fake({"/sedzia": {"silniejsza_idx": 1, "silniejsza": "b"}})
        self.assertTrue(self.c.lepsza("A" * 800, "C" * 800))
        self.c.wolaj = self._fake({"/sedzia": {"silniejsza_idx": 0, "silniejsza": "a"}})
        self.assertFalse(self.c.lepsza("A" * 800, "C" * 800))

    def test_turniej_zwraca_tylko_zwyciezcow(self):
        def sedzia(dane):
            return {"silniejsza_idx": 1 if dane["nazwa_b"] == "dobry" else 0}

        self.c.wolaj = self._fake({"/sedzia": sedzia})
        # nazwa_b w turniej() to domyslne "b", wiec podmieniamy na wersje po etykiecie
        self.c.lepsza = lambda a, b: b.startswith("G")
        wygrane = self.c.turniej(BAZA, {"x": "A" * 800, "y": "G" * 800})
        self.assertEqual([e for e, _ in wygrane], ["y"])

    def test_ranking_swiss_uklada_od_najlepszego(self):
        # "lepsza" = wiecej G w sekwencji
        self.c.lepsza = lambda a, b: b.count("G") > a.count("G")
        kandydaci = {
            "slaby": "A" * 800,
            "sredni": "G" * 400 + "A" * 400,
            "mocny": "G" * 800,
            "zerowy": "T" * 800,
        }
        wynik = self.c.ranking_swiss(kandydaci, rund=4)
        self.assertEqual(wynik[0][0], "mocny")
        self.assertEqual(len(wynik), 4)
        self.assertEqual(sum(p for _, p, _ in wynik), 4 * 2)  # 2 pary x 4 rundy


class TestTransport(unittest.TestCase):
    def _odp(self, tresc):
        o = mock.MagicMock()
        o.status = 200
        o.read.return_value = json.dumps(tresc).encode()
        o.__enter__.return_value = o
        o.__exit__.return_value = False
        return o

    def _blad(self, kod, retry_after=None):
        naglowki = {"Retry-After": retry_after} if retry_after else {}
        e = urllib.error.HTTPError(
            "u", kod, "err", naglowki, io.BytesIO(b'{"detal":"nie"}'))
        self.addCleanup(e.close)
        return e

    def test_get_bez_body(self):
        c = klient(przestrzegaj_limitow=False)
        with mock.patch("urllib.request.urlopen", return_value=self._odp({"ok": 1})) as u:
            self.assertEqual(c.wolaj("/me"), (200, {"ok": 1}))
        self.assertIsNone(u.call_args[0][0].data)

    def test_post_wysyla_json_i_naglowki(self):
        c = klient(przestrzegaj_limitow=False)
        with mock.patch("urllib.request.urlopen", return_value=self._odp({"ok": 1})) as u:
            c.wolaj("/sedzia", {"a": "A", "b": "C"})
        req = u.call_args[0][0]
        self.assertEqual(json.loads(req.data), {"a": "A", "b": "C"})
        self.assertEqual(req.get_header("X-api-key"), "test")
        self.assertIn("Mozilla", req.get_header("User-agent"))

    def test_ponawia_503(self):
        c = klient(przestrzegaj_limitow=False)
        efekty = [self._blad(503), self._blad(503), self._odp({"ok": 1})]
        with mock.patch("urllib.request.urlopen", side_effect=efekty), \
                mock.patch("time.sleep"):
            self.assertEqual(c.wolaj("/sedzia", {"a": 1})[0], 200)

    def test_nie_ponawia_429_na_wgraj(self):
        c = klient(przestrzegaj_limitow=False)
        with mock.patch("urllib.request.urlopen", side_effect=self._blad(429)) as u, \
                mock.patch("time.sleep"):
            kod, _ = c.wolaj("/wgraj", {"fasta": ">a\nACGT"})
        self.assertEqual(kod, 429)
        self.assertEqual(u.call_count, 1, "wgraj nie powinno bic w limit 5 min")

    def test_ponawia_429_na_sedzi(self):
        c = klient(przestrzegaj_limitow=False)
        efekty = [self._blad(429, "0.01"), self._odp({"ok": 1})]
        with mock.patch("urllib.request.urlopen", side_effect=efekty), \
                mock.patch("time.sleep"):
            self.assertEqual(c.wolaj("/sedzia", {"a": 1})[0], 200)

    def test_422_nie_jest_ponawiane(self):
        c = klient(przestrzegaj_limitow=False)
        with mock.patch("urllib.request.urlopen", side_effect=self._blad(422)) as u:
            kod, tresc = c.wolaj("/sedzia", {"a": 1})
        self.assertEqual((kod, u.call_count), (422, 1))
        self.assertEqual(tresc, {"detal": "nie"})

    def test_ok_rzuca_apierror(self):
        c = klient(przestrzegaj_limitow=False)
        with mock.patch("urllib.request.urlopen", side_effect=self._blad(403)):
            with self.assertRaises(ApiError) as ctx:
                c.me()
        self.assertEqual(ctx.exception.kod, 403)


class TestRateLimiter(unittest.TestCase):
    def test_przepuszcza_do_limitu_bez_czekania(self):
        rl = RateLimiter(3)
        with mock.patch("time.sleep") as s:
            for _ in range(3):
                rl.czekaj()
        s.assert_not_called()

    def test_czeka_po_przekroczeniu(self):
        rl = RateLimiter(2)
        rl.czekaj()
        rl.czekaj()
        with mock.patch("time.sleep") as s:
            s.side_effect = lambda _: rl._czasy.clear()
            rl.czekaj()
        s.assert_called_once()

    def test_zero_wylacza_limiter(self):
        rl = RateLimiter(0)
        with mock.patch("time.sleep") as s:
            for _ in range(1000):
                rl.czekaj()
        s.assert_not_called()


class TestKonfiguracja(unittest.TestCase):
    def test_brak_klucza_rzuca_czytelny_blad(self):
        with mock.patch.dict("os.environ", {"HYPPE_API_KEY": ""}, clear=False), \
                mock.patch("hyppe.config.load_dotenv", return_value={}):
            with self.assertRaises(RuntimeError) as ctx:
                Config.from_env()
        self.assertIn("HYPPE_API_KEY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
