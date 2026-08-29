"""Sciezki, klient, zapis wynikow.

Zasada: `zapisz` NIGDY nie nadpisuje po cichu. Jesli `wyniki.json` istnieje,
stary plik laduje w `archiwum/wyniki_<timestamp>.json`. W trakcie hackathonu
przypadkowe nadpisanie pomiaru, ktory kosztowal 5 minut, boli bardziej niz
kilka plikow wiecej na dysku.
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KATALOG = REPO / "eksperymenty"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def klient(**kw):
    """Klient hyppe z .env. Import lokalny, zeby modul dal sie zaimportowac
    w notebooku bez klucza API."""
    from hyppe import Client

    return Client.from_env(**kw)


def zapisz(sciezka: Path | str, dane: dict, *, archiwizuj: bool = True) -> Path:
    """Zapisuje JSON, archiwizujac poprzednia wersje. Zwraca sciezke."""
    p = Path(sciezka)
    p.parent.mkdir(parents=True, exist_ok=True)
    if archiwizuj and p.exists():
        stempel = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        arch = p.parent / "archiwum"
        arch.mkdir(exist_ok=True)
        p.replace(arch / f"{p.stem}_{stempel}{p.suffix}")
    dane.setdefault("_zebrano", _dt.datetime.now().isoformat(timespec="seconds"))
    p.write_text(json.dumps(dane, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def wczytaj(sciezka: Path | str) -> dict | None:
    """Wczytuje JSON albo zwraca None, jesli pliku nie ma.

    Notebooki uzywaja tego, zeby pominac sekcje eksperymentow, ktore jeszcze
    nie zostaly uruchomione -- notebook ma sie budowac w trakcie pracy.
    """
    p = Path(sciezka)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
