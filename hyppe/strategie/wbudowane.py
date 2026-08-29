"""Strategie wbudowane -- punkt wyjscia. Wlasne pomysly wrzucajcie do
osobnych plikow w tym katalogu (patrz `__init__.py`).
"""

from __future__ import annotations

import random

from . import strategia
from ..client import Client
from ..seq import krzyzuj, mutuj


@strategia("nawigator")
def pula_nawigator(
    c: Client, baza: str, ile: int = 100, poziom: int = 2, opcji: int = 8, **_
) -> dict[str, str]:
    """Warianty z /nawigator/edycje przy rosnacej liczbie zmienianych kodow."""
    pula: dict[str, str] = {}
    mapa = c.mapa(baza)
    z_mapy = c.zastosuj_rekomendacje(baza, mapa)
    if z_mapy != baza:
        pula[z_mapy] = "z_mapy"
    for runda in range(1, 40):
        if len(pula) >= ile:
            break
        e = c.edycje(
            baza, poziom=poziom, ile_kodow=6 + runda, opcji=opcji, ziarno=1000 + runda
        )
        for o in e["opcje"]:
            pula.setdefault(o["sekwencja"], f"nav_r{runda}_{o['nr']}")
    return {etyk: seq for seq, etyk in list(pula.items())[:ile]}


@strategia("mutacje")
def pula_mutacje(
    c: Client, baza: str, ile: int = 100, sila: int = 8, tylko_swobodne: bool = True, ziarno: int = 7, **_
) -> dict[str, str]:
    """Losowe podstawienia, domyslnie tylko na pozycjach `rekon == 0`.

    Pozycje z rekon=1 i zerowymi warstwami i tak nadpisze dekoder, wiec
    mutowanie ich to marnowanie budzetu.
    """
    r = random.Random(ziarno)
    pozycje = None
    if tylko_swobodne:
        m = c.mapa(baza)
        pozycje = [w["poz"] for w in m["pozycje"] if w["rekon"] == 0] or None
    out: dict[str, str] = {}
    proby = 0
    while len(out) < ile and proby < ile * 20:
        proby += 1
        n = r.randint(max(1, sila // 2), sila * 2)
        seq = mutuj(baza, ile=n, pozycje=pozycje, rng=r)
        if seq != baza:
            out.setdefault(f"mut_{len(out):03d}_n{n}", seq)
    return out


@strategia("hybryda")
def pula_hybryda(
    c: Client, baza: str, ile: int = 100, poziom: int = 2, ziarno: int = 11, **_
) -> dict[str, str]:
    """Polowa z Nawigatora, polowa z krzyzowania zwyciezcow Sedziego."""
    r = random.Random(ziarno)
    nav = pula_nawigator(c, baza, ile=max(8, ile // 2), poziom=poziom)
    wygrane = c.turniej(baza, nav)
    rodzice = [s for _, s in wygrane] or list(nav.values())
    out = dict(nav)
    prob = 0
    while len(out) < ile and prob < ile * 20 and len(rodzice) >= 2:
        prob += 1
        a, b = r.sample(rodzice, 2)
        dziecko = mutuj(krzyzuj(a, b, punktow=r.randint(1, 4), rng=r), ile=r.randint(0, 6), rng=r)
        if dziecko not in out.values():
            out[f"hyb_{len(out):03d}"] = dziecko
    return out
