"""Rejestr strategii generowania puli kandydatow.

Kazdy plik `.py` w tym katalogu jest importowany automatycznie, wiec
**kazda osoba w zespole moze miec wlasny plik** i nikt nikomu nie wchodzi
w drogi (brak konfliktow w gicie).

    # hyppe/strategie/julian.py
    from . import strategia

    @strategia("julian-tata")
    def moja(c, baza, ile=100, **_):
        ...
        return {"etykieta": "ACGT...", ...}

Potem:  python -m hyppe pula --strategia julian-tata
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Callable

REJESTR: dict[str, Callable[..., dict[str, str]]] = {}


def strategia(nazwa: str):
    """Dekorator rejestrujacy funkcje (Client, baza, **opcje) -> {etykieta: seq}."""

    def dekorator(fn):
        if nazwa in REJESTR:
            raise KeyError(f"strategia '{nazwa}' juz istnieje ({REJESTR[nazwa].__module__})")
        REJESTR[nazwa] = fn
        fn.nazwa_strategii = nazwa
        return fn

    return dekorator


def uruchom(nazwa: str, c, baza: str, **opcje) -> dict[str, str]:
    if nazwa not in REJESTR:
        raise KeyError(f"nieznana strategia: {nazwa}. Dostepne: {', '.join(sorted(REJESTR))}")
    return REJESTR[nazwa](c, baza, **opcje)


def _zaladuj_wszystkie() -> None:
    for mod in pkgutil.iter_modules(__path__):
        if not mod.name.startswith("_"):
            importlib.import_module(f"{__name__}.{mod.name}")


_zaladuj_wszystkie()
