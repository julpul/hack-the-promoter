#!/usr/bin/env python3
"""Wykresy do prezentacji. Wszystko z plikow `wyniki*.json` w eksperymentach.

    .venv/bin/python presentation/wykresy.py
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
WY = Path(__file__).resolve().parent / "wykresy"
WY.mkdir(parents=True, exist_ok=True)

# Paleta referencyjna (tryb jasny), zwalidowana skryptem validate_palette.js:
# 3 sloty, wszystkie pary PASS. Aqua ma kontrast < 3:1, wiec wszedzie
# stosujemy etykiety bezposrednie (regula reliefu).
NIEBIESKI, POMARANCZ, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TEKST, DRUGI, SZARY = "#0b0b0b", "#52514e", "#c9c8c3"
TLO = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": TLO, "axes.facecolor": TLO,
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11,
    "axes.edgecolor": SZARY, "axes.labelcolor": DRUGI,
    "xtick.color": DRUGI, "ytick.color": DRUGI,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 140,
})


def wczytaj(sciezka: str):
    p = REPO / sciezka
    return json.loads(p.read_text()) if p.exists() else None


# --- 1. Historia zgloszen ----------------------------------------------------
# Jedna seria (magnitude) -> jeden kolor; nasz najlepszy wyrozniony.
ZGLOSZENIA = [                       # (etykieta, punkty, rodzaj)
    ("v11_B2 — chimery z obcego promotora", 4.0, "zle"),
    ("v9_B0 — linia bazowa: dziki + 1 podstawienie", 5.0, "baza"),
    ("v10_B1 — trakty poli(dA:dT)", 8.0, "zwykle"),
    ("v16 — pokolenia pchniete dalej (dyst. 192–262)", 11.0, "zwykle"),
    ("v8 — ziarna + CCAAT", 12.0, "zwykle"),
    ("v15 — czysta glebokosc (100 x najglebsze)", 12.0, "zwykle"),
    ("w18 — piec rodzin po 20", 12.0, "zwykle"),
    ("v22 — izolowany pas optymalny", 12.0, "zwykle"),
    ("v14 — TEN SAM PLIK, ponownie o 19:55", 12.0, "dryf"),
    ("v14 — glebokosc + pokolenia, o 18:52", 14.0, "best"),
]


def wykres_historia():
    fig, ax = plt.subplots(figsize=(10.2, 5.0))
    etyk = [e for e, _, _ in ZGLOSZENIA]
    war = [w for _, w, _ in ZGLOSZENIA]
    barwy = {"best": POMARANCZ, "dryf": POMARANCZ, "baza": SZARY,
             "zle": SZARY, "zwykle": NIEBIESKI}
    kol = [barwy[t] for _, _, t in ZGLOSZENIA]
    y = range(len(war))
    slupki = ax.barh(list(y), war, color=kol, height=0.66, zorder=3)
    for s, (e, w, t) in zip(slupki, ZGLOSZENIA):
        ax.text(w + 0.18, s.get_y() + s.get_height() / 2, f"{w:.1f}",
                ha="left", va="center", fontsize=11, color=TEKST,
                fontweight="bold")
        if t == "dryf":
            # Slupek kontrolny: rysujemy go w kolorze v14, ale w paski,
            # zeby bylo widac, ze to ta sama sekwencja, inny odczyt.
            s.set_hatch("///")
            s.set_edgecolor(TLO)
            s.set_linewidth(0)
    ax.axvline(5.0, color=SZARY, lw=1.5, ls="--", zorder=2)
    ax.set_yticks(list(y))
    ax.set_yticklabels(etyk, fontsize=9.5)
    ax.set_xlabel("punkty w rankingu (TOP10 + ALL100)")
    ax.set_xlim(0, 16)
    ax.set_title("Ten sam plik, dwa odczyty: 14,0 i 12,0.\n"
                 "Ranking punktuje range, a pole rusza sie pod nami",
                 color=TEKST, loc="left", pad=12)
    ax.annotate("", xy=(13.85, 9.0), xytext=(11.85, 8.0),
                arrowprops=dict(arrowstyle="<->", color=POMARANCZ, lw=1.8,
                                shrinkA=0, shrinkB=0))
    ax.text(11.7, 7.15, "ten sam plik, 63 min pozniej — dryf pola",
            fontsize=10, color=POMARANCZ, fontweight="bold", ha="right")
    ax.grid(axis="x", color=SZARY, lw=0.6, alpha=0.5, zorder=0)
    fig.tight_layout()
    fig.savefig(WY / "1_historia.png", bbox_inches="tight")
    plt.close(fig)


# --- 2. Mapa rodzin ----------------------------------------------------------
def wykres_rodziny():
    przesiew = wczytaj("eksperymenty/E14_kompozycja/wyniki_przesiew.json")
    e13 = wczytaj("eksperymenty/E13_glebokosc/wyniki.json")
    pas = wczytaj("eksperymenty/E14_kompozycja/wyniki_pas.json")
    pok16 = wczytaj("eksperymenty/E14_kompozycja/wyniki_pokolenia.json")
    if not (przesiew and e13):
        print("brak danych do wykresu 2"); return

    # Male wielokrotnosci: jedna rodzina na panel, ten sam uklad osi.
    # Kazdy panel ma jedna serie, wiec problem rozroznialnosci kolorow
    # w ogole nie powstaje, a porownanie idzie po polozeniu.
    panele = [("v14 blok A\nglebokie ziarna", e13["blok_A"], "14,0"),
              ("v14 blok B\npokolenia z plytkich", e13["blok_B"], "14,0")]
    if pas:
        panele.append(("v22 pas optymalny\nizolowana rodzina B", pas["wybor"],
                       "12,0"))
    if pok16:
        panele.append(("v16 blok B\npokolenia z glebokich", pok16["blok_B"],
                       "11,0"))

    tlo = przesiew["pula"]
    fig, osie = plt.subplots(2, 2, figsize=(10.5, 6.4), sharex=True,
                             sharey=True)
    for ax, (nazwa, dane, pkt) in zip(osie.ravel(), panele):
        ax.axvspan(180, 280, color=POMARANCZ, alpha=0.08, zorder=1)
        ax.axvline(180, color=POMARANCZ, lw=1.3, ls="--", zorder=2)
        ax.scatter([x["dystans"] for x in tlo],
                   [x["blad_odtworzenia"] for x in tlo],
                   s=9, color=SZARY, alpha=0.55, linewidths=0, zorder=3)
        za_sciana = sum(1 for x in dane if x["dystans"] > 180)
        ax.scatter([x["dystans"] for x in dane],
                   [x["blad_odtworzenia"] for x in dane],
                   s=26, color=POMARANCZ if za_sciana > len(dane) / 2
                   else NIEBIESKI,
                   alpha=0.9, linewidths=0.6, edgecolors=TLO, zorder=4)
        ax.set_title(f"{nazwa}   —   {pkt} pkt", fontsize=10.5, loc="left",
                     color=TEKST, pad=6)
        ax.grid(color=SZARY, lw=0.5, alpha=0.4, zorder=0)
    osie[0][0].set_xlim(85, 280)
    osie[0][0].set_ylim(-2, 42)
    for ax in osie[1]:
        ax.set_xlabel("dystans od dzikiego (pz)")
    for ax in (osie[0][0], osie[1][0]):
        ax.set_ylabel("blad_odtworzenia")
    osie[1][1].text(186, 40, "sciana ~180 pz", ha="left", va="top",
                    fontsize=9.5, color=POMARANCZ, fontweight="bold")
    osie[0][1].text(96, 40, "szare: 603 kandydatow\nz przesiewu",
                    ha="left", va="top", fontsize=9, color=DRUGI)
    fig.suptitle("Ta sama rodzina, ten sam pas — a wynik inny. "
                 "Zadna os osobno nie tlumaczy 14,0",
                 fontsize=13, color=TEKST, x=0.012, ha="left", y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    fig.savefig(WY / "2_rodziny.png", bbox_inches="tight")
    plt.close(fig)


# --- 3. Strojenie zrodla -----------------------------------------------------
def wykres_zrodlo():
    d = wczytaj("eksperymenty/E14_kompozycja/wyniki_przesiew.json")
    if not d:
        print("brak danych do wykresu 3"); return
    kody = sorted({w["ile_kodow"] for w in d["zrodlo"]})
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    szer = 0.38
    for i, (poziom, kolor) in enumerate(((1, NIEBIESKI), (2, POMARANCZ))):
        war = []
        for k in kody:
            t = [w for w in d["zrodlo"]
                 if w["poziom"] == poziom and w["ile_kodow"] == k]
            war.append(t[0]["przelotowosc"] if t else 0.0)
        poz = [j + (i - 0.5) * (szer + 0.02) for j in range(len(kody))]
        ax.bar(poz, war, width=szer, color=kolor, zorder=3,
               label=f"poziom {poziom}")
        for x, w in zip(poz, war):
            ax.text(x, w + 0.25, f"{w:.1f}", ha="center", va="bottom",
                    fontsize=9, color=TEKST)
    ax.set_xticks(range(len(kody)))
    ax.set_xticklabels([str(k) for k in kody])
    ax.set_xlabel("ile_kodow  (parametr /nawigator/edycje)")
    ax.set_ylabel("% kandydatow, ktorzy przeszli bramke Sedziego")
    ax.set_title("Strojenie zrodla: poziom 2 z wysokim ile_kodow przepuszcza 5x wiecej",
                 color=TEKST, loc="left", pad=12)
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.grid(axis="y", color=SZARY, lw=0.6, alpha=0.5, zorder=0)
    fig.tight_layout()
    fig.savefig(WY / "3_zrodlo.png", bbox_inches="tight")
    plt.close(fig)


# --- 4. Elementy cis ---------------------------------------------------------
def wykres_cis():
    sys.path.insert(0, str(REPO / "eksperymenty" / "E14_kompozycja"))
    sys.path.insert(0, str(REPO))
    import strategie as B
    from hyppe import fasta as F

    v14 = F.czytaj(REPO / "runs" / "julian" / "v14_glebokosc.fasta")
    w17 = REPO / "runs" / "julian" / "w17_pelna_kompozycja.fasta"
    przed = B.policz_elementy(v14[0].seq)
    po = B.policz_elementy(F.czytaj(w17)[0].seq) if w17.exists() else None

    elementy = ["CCAAT", "GGCTAA", "Cre1"]
    opisy = ["CCAAT\n(Hap2/3/5, aktywator)", "GGCTAA\n(Xyr1/ACE2, aktywator)",
             "SYGGRG\n(Cre1, REPRESOR)"]
    serie = [("dziki / nasz podklad", [przed[e] for e in elementy], NIEBIESKI),
             ("mediana 100 naturalnych", [2, 0, 2], AQUA)]
    if po:
        serie.append(("po zlozeniu blokow", [po[e] for e in elementy], POMARANCZ))

    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    szer = 0.8 / len(serie)
    for i, (nazwa, war, kolor) in enumerate(serie):
        poz = [j + (i - (len(serie) - 1) / 2) * (szer + 0.02)
               for j in range(len(elementy))]
        ax.bar(poz, war, width=szer, color=kolor, zorder=3, label=nazwa)
        for x, w in zip(poz, war):
            ax.text(x, w + 0.08, str(w), ha="center", va="bottom",
                    fontsize=10, color=TEKST, fontweight="bold")
    ax.set_xticks(range(len(elementy)))
    ax.set_xticklabels(opisy, fontsize=9.5)
    ax.set_ylabel("liczba miejsc wiazania (obie nici)")
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_ylim(0, 5.2)
    ax.set_title("Dziki pks1 nie ma dwoch aktywatorow — percentyl 0 % wobec rodzaju",
                 color=TEKST, loc="left", pad=12)
    ax.legend(frameon=False, fontsize=10, loc="upper left",
              bbox_to_anchor=(0.005, 1.0))
    ax.grid(axis="y", color=SZARY, lw=0.6, alpha=0.5, zorder=0)
    fig.tight_layout()
    fig.savefig(WY / "4_cis.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    wykres_historia()
    wykres_rodziny()
    wykres_zrodlo()
    wykres_cis()
    for p in sorted(WY.glob("*.png")):
        print("zapisano", p.relative_to(REPO))
