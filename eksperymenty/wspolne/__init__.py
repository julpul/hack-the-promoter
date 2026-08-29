"""Wspolne narzedzia eksperymentow fazy 2.

Trzy moduly:
    io        - sciezki, zapis/odczyt wyniki.json bez cichego nadpisywania
    kandydaci - budowanie baterii sekwencji kontrolnych (shuffle, rotacja, ...)
    metryki   - ekstrakcja skalarow z odpowiedzi /nawigator/mapa

Zaleznosci: wylacznie stdlib + hyppe. `numpy`/`pandas`/`seaborn` sa uzywane
tylko w notebookach, nigdy w `run.py` -- zeby zbieranie danych dzialalo
na golym Pythonie nawet gdy komus padnie venv w trakcie hackathonu.
"""

from .io import KATALOG, REPO, klient, wczytaj, zapisz
from .kandydaci import (
    GC_DZIKIEGO,
    losowa,
    obroc,
    odwroc,
    podmien_okno,
    przetasuj,
    wczytaj_naturalne,
    wczytaj_pule,
)
from .metryki import RDZEN_DO, RDZEN_OD, metryki_mapy, srodek_masy

__all__ = [
    "KATALOG", "REPO", "klient", "wczytaj", "zapisz",
    "GC_DZIKIEGO", "losowa", "obroc", "odwroc", "podmien_okno", "przetasuj",
    "wczytaj_naturalne", "wczytaj_pule",
    "RDZEN_OD", "RDZEN_DO", "metryki_mapy", "srodek_masy",
]
