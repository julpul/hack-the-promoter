#!/usr/bin/env python3
"""Trzy proste diagramy pod `SCENARIUSZ.md` — do czytania z sali.

Zasada: jeden diagram niesie jedno zdanie. Duze liczby, malo tuszu,
zadnych legend (kazdy element podpisany bezposrednio).

Techniczne wersje tych samych danych leza w `wykresy.py` — tamte sa
do backupu i na pytania z sali.

    .venv/bin/python presentation/wykresy_proste.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

WY = Path(__file__).resolve().parent / "wykresy"
WY.mkdir(parents=True, exist_ok=True)

NIEBIESKI, POMARANCZ = "#2a78d6", "#eb6834"
TEKST, DRUGI, SZARY, TLO = "#0b0b0b", "#52514e", "#c9c8c3", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": TLO, "axes.facecolor": TLO,
    "axes.edgecolor": SZARY, "axes.labelcolor": DRUGI,
    "xtick.color": DRUGI, "ytick.color": DRUGI,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150,
})


def d1_narzedzia():
    """Slajd 2 — dwie liczby, ktore podwazyly oba narzedzia."""
    fig, osie = plt.subplots(1, 2, figsize=(11, 4.4))
    kafle = [
        (osie[0], "0", "z 180", "Sedzia",
         "Tyle prawdziwych i losowych sekwencji\npobilo nasz oryginal.\n"
         "Sedzia nie ocenia sily — rozpoznaje,\nczy cos wyglada jak promotor.",
         NIEBIESKI),
        (osie[1], "100", "ze 101", "Mapa modelu",
         "Tyle sekwencji ma szczyt uwagi\nw tym samym punkcie — takze te\n"
         "obrocone, pomieszane i losowe.\nTo artefakt, nie biologia.",
         POMARANCZ),
    ]
    for ax, duza, mala, tytul, opis, kolor in kafle:
        ax.axis("off")
        # Mianownik idzie POD liczba, nie obok — inaczej "100" wchodzi
        # na swoj podpis, bo szerokosc cyfr jest rozna w kazdym kaflu.
        ax.text(0.0, 0.99, tytul, fontsize=15, color=DRUGI, va="top",
                fontweight="bold")
        ax.text(0.0, 0.84, duza, fontsize=80, color=kolor, va="top",
                fontweight="bold", linespacing=0.8)
        ax.text(0.0, 0.40, mala, fontsize=22, color=SZARY, va="top")
        ax.text(0.0, 0.26, opis, fontsize=13, color=TEKST, va="top",
                linespacing=1.5)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    fig.suptitle("Zanim cokolwiek zaprojektowalismy — sprawdzilismy przyrzady",
                 fontsize=17, color=TEKST, x=0.045, ha="left", y=1.04)
    fig.tight_layout()
    fig.savefig(WY / "s2_narzedzia.png", bbox_inches="tight")
    plt.close(fig)


def d2_przelom():
    """Slajd 4 — linia zero i to, co dopiero dzieki niej bylo widac."""
    dane = [
        ("Wymieszane z prawdziwymi\npromotorami z natury", 4.0, SZARY),
        ("LINIA ZERO\noryginal + jedna zmieniona litera", 5.0, POMARANCZ),
        ("Nasz najlepszy plik", 14.0, NIEBIESKI),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 4.0))
    y = range(len(dane))
    slupki = ax.barh(list(y), [w for _, w, _ in dane],
                     color=[k for _, _, k in dane], height=0.58, zorder=3)
    for s, (_, w, _) in zip(slupki, dane):
        ax.text(w + 0.25, s.get_y() + s.get_height() / 2, f"{w:.0f}",
                ha="left", va="center", fontsize=22, color=TEKST,
                fontweight="bold")
    ax.set_yticks(list(y))
    ax.set_yticklabels([e for e, _, _ in dane], fontsize=12)
    ax.set_xlim(0, 16.5)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_title("Przez pol dnia wygladalo, ze nic nie dziala.\n"
                 "Brakowalo punktu odniesienia — nie wynikow",
                 fontsize=17, color=TEKST, loc="left", pad=16)
    ax.annotate("", xy=(14.0, 2.42), xytext=(5.0, 2.42),
                arrowprops=dict(arrowstyle="<->", color=DRUGI, lw=1.6))
    ax.text(9.5, 2.55, "piec miejsc w rankingu", fontsize=12.5, color=DRUGI,
            ha="center", fontweight="bold")
    ax.set_ylim(-0.55, 2.95)
    fig.tight_layout()
    fig.savefig(WY / "s4_przelom.png", bbox_inches="tight")
    plt.close(fig)


def d3_dryf():
    """Slajd 5 — ten sam plik, dwa odczyty."""
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    etyk = ["wyslany o 18:52", "wyslany o 19:55"]
    war = [14.0, 12.0]
    slupki = ax.bar(etyk, war, color=[POMARANCZ, POMARANCZ], width=0.42,
                    zorder=3)
    slupki[1].set_hatch("///")
    slupki[1].set_edgecolor(TLO)
    for s, w in zip(slupki, war):
        ax.text(s.get_x() + s.get_width() / 2, w + 0.3, f"{w:.0f}",
                ha="center", va="bottom", fontsize=34, color=TEKST,
                fontweight="bold")
    ax.set_ylim(0, 17.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", labelsize=14)
    ax.set_title("Ten sam plik. Te same sekwencje. Nizszy wynik.\n"
                 "Ranking punktuje MIEJSCE, nie wartosc",
                 fontsize=17, color=TEKST, loc="left", pad=16)
    ax.text(0.5, 8.2, "w miedzyczasie\ninne druzyny\nwyslaly swoje",
            ha="center", va="center", fontsize=13, color=DRUGI,
            linespacing=1.6)
    ax.annotate("", xy=(0.88, 12.6), xytext=(0.12, 14.6),
                arrowprops=dict(arrowstyle="->", color=DRUGI, lw=1.8,
                                connectionstyle="arc3,rad=-0.25"))
    fig.tight_layout()
    fig.savefig(WY / "s5_dryf.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    d1_narzedzia()
    d2_przelom()
    d3_dryf()
    for p in sorted(WY.glob("s*.png")):
        print("zapisano", p.name)
