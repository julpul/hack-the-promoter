#!/usr/bin/env python3
"""Buduje eksperymenty/eksperymenty.ipynb z sekcji zdefiniowanych ponizej.

Notebook trzymamy jako skrypt (konwencja z scripts/zbuduj_notebook.py) -- .ipynb
zle sie merguje w gicie.

Sekcje eksperymentow, ktore nie maja jeszcze wyniki.json, sa POMIJANE, wiec
notebook da sie budowac w trakcie pracy i przybywa mu rozdzialow.

    .venv/bin/python eksperymenty/zbuduj_notebook.py
    .venv/bin/jupyter lab eksperymenty/eksperymenty.ipynb
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat as nbf

TU = Path(__file__).resolve().parent
WYJSCIE = TU / "eksperymenty.ipynb"

KOMORKI: list[tuple[str, str]] = []
md = lambda t: KOMORKI.append(("md", t.strip()))          # noqa: E731
kod = lambda t: KOMORKI.append(("kod", t.strip()))        # noqa: E731


def jest(nazwa: str) -> bool:
    return (TU / nazwa / "wyniki.json").exists()


# ═══════════════════════════════════════════════════════════════════════════
md(r"""
# Hack the Promoter — faza 2: szukanie funkcji celu

**iGEM Warsaw 2026 · drużyna_01**

Faza 1 (`hipotezy.ipynb`) odpowiedziała na pytanie **czego te modele nie umieją**:
sześć z siedmiu hipotez obalonych, Sędzia wysycony, przestrzeń liter martwa.
Ta faza odpowiada na pytanie **czego da się użyć zamiast tego**.

Punkt wyjścia to jedno zdanie z komórki 29 fazy 1: *„chciałbyś funkcję straty
L(x), masz komparator a-czy-b"*. Cała bezradność optymalizacji brała się z tego
wiersza. **E01 sprawdza, czy ten wiersz jest prawdziwy.**

## Plan

| # | pytanie | rola |
|---|---|---|
| E01 | Czy nagłówek `/mapa` zawiera porównywalny skalar? | blokujący — daje albo nie daje funkcji celu |
| E02 | Czy szczyt `wagaP` idzie za treścią, czy siedzi na krawędzi? | blokujący — waliduje 30 % planu zgłoszenia |
| E03 | Co jest w stu naturalnych promotorach *Trichoderma*? | jedyne dane spoza modelu |
| E04 | Jak składają się cztery hipotezy? (plan faktorialny 2⁴) | konstrukcyjny |
| E05 | Jak z tego złożyć 100 sekwencji? | zgłoszenie |

Szczegóły i uzasadnienia: `PLAN.md` w każdym katalogu. Wnioski: `WNIOSKI.md`.
""")

kod(r"""
import json, sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

TU = Path.cwd() if Path.cwd().name == "eksperymenty" else Path.cwd() / "eksperymenty"
sys.path.insert(0, str(TU.parent))

from eksperymenty.wspolne import metryki as M
from hyppe import seq as S

sns.set_theme(style="whitegrid", context="notebook")
sns.set_palette("deep")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["figure.autolayout"] = True

def wczytaj(nazwa):
    p = TU / nazwa / "wyniki.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

def ramka_metryk(rekordy, dodatkowe=()):
    w = []
    for r in rekordy:
        d = {"etykieta": r.get("etykieta") or r.get("nazwa"), "grupa": r.get("grupa")}
        d.update(r.get("metryki") or {})
        for k in dodatkowe:
            d[k] = r.get(k)
        d.pop("pozycje_rekomendacji", None)
        w.append(d)
    return pd.DataFrame(w)

print("gotowe")
""")

# ── E01 ────────────────────────────────────────────────────────────────────
if jest("E01_funkcja_celu"):
    md(r"""
---
# E01 · Czy nagłówek `/mapa` zawiera funkcję celu?

Legenda API zastrzega nieporównywalność między sekwencjami **wyłącznie dla
`wagaP`**. Cztery inne pola nagłówka to bezwzględne liczby:

```
zmian_pod_gatunek    ile pozycji kanał gatunku chce jeszcze zmienić pod P1
blad_odtworzenia     bezwzględny błąd rekonstrukcji tej sekwencji
nie_rekonstruuje     ile pozycji nie odtwarza się z samych kodów
rekon_frakcja        udział pozycji odtwarzanych
```

Jeśli wariują — mamy skalar do minimalizowania i wraca wspinaczka, która
w fazie 1 padła wyłącznie przez wysycone kryterium (H6).
""")

    kod(r"""
w01 = wczytaj("E01_funkcja_celu")
df01 = ramka_metryk(w01["rekordy"], dodatkowe=("dystans_od_dzikiego", "bije_dzikiego", "opis"))

kandydaci = ["blad_odtworzenia", "zmian_pod_gatunek", "nie_rekonstruuje", "rekon_frakcja"]
print("WARIANCJA POL KANDYDUJACYCH (bez powtorzen):")
bez_powt = df01[df01["grupa"] != "powtorzenie"]
for k in kandydaci:
    if k in df01 and df01[k].notna().any():
        s = bez_powt[k]
        print(f"  {k:<20} min={s.min():>8} max={s.max():>8} "
              f"std={s.std():>7.2f} unikalnych={s.nunique():>3}")

print("\nDETERMINIZM (ten sam dziki, 5 wywolan):")
powt = df01[df01["grupa"].isin(["odniesienie", "powtorzenie"])]
for k in kandydaci:
    if k in powt and powt[k].notna().any():
        print(f"  {k:<20} {sorted(powt[k].tolist())}  -> "
              f"{'DETERMINISTYCZNE' if powt[k].nunique() == 1 else 'NIEDETERMINISTYCZNE'}")
""")

    kod(r"""
dostepne = [k for k in ("blad_odtworzenia", "zmian_pod_gatunek")
            if k in df01 and df01[k].notna().any()]
fig, axs = plt.subplots(1, len(dostepne), figsize=(6.5 * len(dostepne), 5), squeeze=False)
for ax, k in zip(axs[0], dostepne):
    sns.stripplot(data=bez_powt, x="grupa", y=k, ax=ax, size=9, jitter=0.22)
    odn = df01.loc[df01["etykieta"] == "dziki", k]
    if len(odn):
        ax.axhline(odn.iloc[0], ls="--", color="#e53e3e", lw=2)
        ax.text(0.01, odn.iloc[0], " dziki", color="#c53030", va="bottom",
                fontsize=9, transform=ax.get_yaxis_transform())
    ax.set(title=f"E01 · {k} — czy jest wariancja?", xlabel="")
    ax.tick_params(axis="x", rotation=35)
plt.show()
""")

    md(r"""
**Jak czytać.** Jeśli punkty w grupie `kontrola_monotonicznosc` (5 / 50 / 200
losowych podstawień) układają się monotonicznie, metryka odtwarza znane
uporządkowanie i nadaje się do sortowania puli. Jeśli wszystkie grupy leżą
na jednej wysokości — pole jest stałe i funkcji celu nie ma.
""")

    kod(r"""
kontrola = df01[df01["grupa"].isin(["odniesienie", "kontrola_monotonicznosc", "kontrola_dolna"])]
if len(kontrola) and dostepne:
    fig, ax = plt.subplots(figsize=(11, 4.6))
    kol = kontrola.sort_values("dystans_od_dzikiego")
    for k in dostepne:
        sns.lineplot(data=kol, x="dystans_od_dzikiego", y=k, marker="o",
                     lw=2.2, markersize=9, ax=ax, label=k)
    ax.set(title="E01 · Monotoniczność na kontroli (znane uporządkowanie a priori)",
           xlabel="liczba zmian od dzikiego", ylabel="wartość metryki", xscale="symlog")
    ax.legend()
    plt.show()
    print(kol[["etykieta", "dystans_od_dzikiego"] + dostepne].to_string(index=False))
""")

    kod(r"""
sedzia = df01[df01["bije_dzikiego"].notna()]
if len(sedzia) and dostepne:
    fig, axs = plt.subplots(1, len(dostepne), figsize=(5.6 * len(dostepne), 4.4), squeeze=False)
    for ax, k in zip(axs[0], dostepne):
        sns.boxplot(data=sedzia, x="bije_dzikiego", y=k, ax=ax, width=0.5)
        sns.stripplot(data=sedzia, x="bije_dzikiego", y=k, ax=ax, color="#2d3748", size=6)
        ax.set(title=f"{k} vs werdykt Sędziego", xlabel="bije dzikiego")
    plt.show()

md_uwaga = '''
NAJLEPSZY MOZLIWY WYNIK to rozdzielenie dla blad_odtworzenia ORAZ BRAK
rozdzielenia dla zmian_pod_gatunek. Dwa proxy sa warte czegos tylko wtedy,
gdy mierza rozne rzeczy -- skorelowane proxy nie wnosi informacji.
Sedzia nie widzi gatunku, wiec niezaleznosc zmian_pod_gatunek od jego
werdyktu POTWIERDZA, ze to osobna os.
'''
print(md_uwaga)
""")

    kod(r"""
num = bez_powt.select_dtypes("number").dropna(axis=1, how="all")
num = num.loc[:, num.nunique() > 1]
if num.shape[1] > 1:
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(num.corr(method="spearman"), annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, ax=ax, cbar_kws={"label": "rho Spearmana"})
    ax.set(title="E01 · Korelacje rangowe metryk — które pola są redundantne")
    plt.show()
""")

# ── E02 ────────────────────────────────────────────────────────────────────
if jest("E02_artefakt_wagap"):
    md(r"""
---
# E02 · Rdzeń promotora czy artefakt brzegowy?

Faza 1 przeznaczyła 30 ze 100 sekwencji na edycję okna 783–800, opierając się
na H1 — i sama zapisała, że nie wie, czy to biologia, czy wrażliwość sieci
konwolucyjnej na krawędź wejścia.

**Rozstrzyga rotacja.** Zachowuje całą treść lokalną i przesuwa ją względem
krawędzi. Jeśli szczyt idzie za treścią → biologia. Jeśli zostaje na końcu →
artefakt. Permutacja i sekwencja losowa to drugi, niezależny tor kontroli.
""")

    kod(r"""
w02 = wczytaj("E02_artefakt_wagap")
df02 = ramka_metryk(w02["rekordy"], dodatkowe=("rotacja", "oczekiwany_szczyt"))
prof = {r["etykieta"]: r["profil_wagaP"] for r in w02["rekordy"]}

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(range(1, 801), prof["dziki"], lw=2.2, color="#1a202c", label="dziki", zorder=5)
for k in w02["rotacje"]:
    e = f"rotacja_{k}"
    if e in prof:
        ax.plot(range(1, 801), prof[e], lw=1.1, alpha=0.85, label=f"rotacja o {k}")
        ocz = df02.loc[df02["etykieta"] == e, "oczekiwany_szczyt"]
        if len(ocz):
            ax.axvline(ocz.iloc[0], ls=":", lw=1.6, alpha=0.7,
                       color=ax.lines[-1].get_color())
ax.axvspan(783, 800, color="#e53e3e", alpha=0.12)
ax.set(title="E02 · Profile wagaP: dziki i rotacje (linie kropkowane = gdzie szczyt POWINIEN wylądować)",
       xlabel="pozycja", ylabel="wagaP", xlim=(1, 800))
ax.legend(ncol=3, fontsize=9)
plt.show()
""")

    kod(r"""
rot = df02[df02["grupa"] == "rotacja"].copy()
odn = df02[df02["etykieta"] == "dziki"]
fig, ax = plt.subplots(figsize=(11, 5))

ks = np.array([0] + sorted(rot["rotacja"].tolist()))
sm0 = odn["srodek_masy"].iloc[0]
ax.plot(ks, [(sm0 - k) % 800 for k in ks], ls="--", lw=2, color="#38a169",
        label="predykcja: sygnał idzie ZA TREŚCIĄ (biologia)")
ax.axhline(sm0, ls="--", lw=2, color="#e53e3e",
           label="predykcja: sygnał siedzi NA KRAWĘDZI (artefakt)")
ax.scatter([0], [sm0], s=220, marker="*", color="#1a202c", zorder=5, label="dziki")
ax.scatter(rot["rotacja"], rot["srodek_masy"], s=150, color="#2b6cb0",
           zorder=5, label="zmierzone")
for _, r in rot.iterrows():
    ax.annotate(f"argmax {int(r['argmax'])}", (r["rotacja"], r["srodek_masy"]),
                textcoords="offset points", xytext=(8, 8), fontsize=9)
ax.set(title="E02 · WERDYKT: środek masy wagaP vs wielkość rotacji",
       xlabel="rotacja (pz)", ylabel="środek masy rozkładu wagaP (pozycja)")
ax.legend()
plt.show()
""")

    kod(r"""
grupy = ["permutacja", "losowa", "rdzen_zniszczony", "naturalny"]
obecne = [g for g in grupy if (df02["grupa"] == g).any()]
fig, axs = plt.subplots(len(obecne), 1, figsize=(13, 2.6 * len(obecne)),
                        sharex=True, squeeze=False)
for ax, g in zip(axs[:, 0], obecne):
    for e in df02.loc[df02["grupa"] == g, "etykieta"]:
        ax.plot(range(1, 801), prof[e], lw=0.9, alpha=0.75)
    ax.plot(range(1, 801), prof["dziki"], lw=1.6, color="#1a202c", alpha=0.55)
    ax.axvspan(783, 800, color="#e53e3e", alpha=0.12)
    ax.set(ylabel="wagaP", title=f"kontrola: {g}  (czarny = dziki)")
axs[-1, 0].set_xlabel("pozycja")
plt.show()

print("SZCZYT NA KONCU (argmax >= 750) wg grupy:")
print(df02.assign(na_koncu=df02["argmax"] >= 750)
        .groupby("grupa")["na_koncu"].agg(["sum", "count"]).to_string())
print("\nJesli permutacja i losowa maja szczyt na koncu -> sygnal nie zalezy od tresci.")
""")

# ── E03 ────────────────────────────────────────────────────────────────────
if jest("E03_naturalne_promotory"):
    md(r"""
---
# E03 · Sto naturalnych promotorów *Trichoderma*

Jedyny zbiór w projekcie, który **nie pochodzi z modelu**. Wszystko inne —
pula `hybryda`, wyjścia `/edycje`, warianty gatunkowe — to wytwory Nawigatora
oceniane przez Sędziego; szukanie w nich korelacji to badanie własnego
generatora. Te sto sekwencji przerywa pętlę.

> Zbiór **nie jest etykietowany siłą** (`data/README.md`: *„to nie jest zestaw
> dobrych odpowiedzi, tylko materiał porównawczy"*). Wolno opisywać strukturę
> i liczyć konsensus; nie wolno nazywać ich „silnymi promotorami".
""")

    kod(r"""
w03 = wczytaj("E03_naturalne_promotory")
nat = pd.DataFrame([{k: v for k, v in r.items() if k not in ("sekwencja", "kmery", "metryki", "motywy", "sklad")}
                    | (r.get("metryki") or {}) for r in w03["rekordy"]])
nat = nat.drop(columns=["pozycje_rekomendacji"], errors="ignore")
print(f"naturalnych: {len(nat)}   bijacych dzikiego: {int(nat['bije_dzikiego'].sum())}")

fig, axs = plt.subplots(1, 3, figsize=(14, 4))
sns.countplot(data=nat, x="bije_dzikiego", ax=axs[0])
axs[0].set(title="Czy bije dzikiego u Sędziego?", xlabel="")
sns.histplot(data=nat, x="dystans_od_dzikiego", bins=25, ax=axs[1])
axs[1].set(title="Dystans Hamminga od dzikiego", xlabel="pozycji różnych")
sns.histplot(data=nat, x="gc", bins=25, ax=axs[2])
axs[2].axvline(0.475, ls="--", color="#e53e3e", lw=2)
axs[2].set(title="GC (czerwona = dziki, 47,5 %)", xlabel="GC")
plt.show()
""")

    kod(r"""
kons = w03["konsensus"]["rdzen"]
dziki = w03["dziki"]
czest = pd.DataFrame([{"poz": k["poz"], **k["czestosci"]} for k in kons["kolumny"]]).set_index("poz")

fig, ax = plt.subplots(figsize=(13, 4.4))
czest.plot(kind="bar", stacked=True, ax=ax, width=0.85,
           color={"A": "#38a169", "C": "#2b6cb0", "G": "#d69e2e", "T": "#e53e3e"})
for i, p in enumerate(czest.index):
    ax.text(i, 1.02, dziki[p - 1], ha="center", fontsize=10, fontweight="bold")
ax.set(title="E03 · Skład zasad w oknie rdzenia 783–800 u 100 naturalnych promotorów "
             "(litery nad słupkami = dziki)",
       xlabel="pozycja", ylabel="częstość", ylim=(0, 1.08))
ax.legend(ncol=4, loc="lower right")
plt.show()

print(f"konsensus naturalnych 783-800 : {kons['konsensus']}")
print(f"dziki             783-800     : {dziki[782:800]}")
print(f"roznic                        : {S.hamming(kons['konsensus'], dziki[782:800])}/18")
print("\n^ to jest tresc czynnika C w E04 -- element rdzeniowy wyprowadzony z danych,")
print("  a nie TATAAA wzięte z podrecznika.")
""")

    kod(r"""
# PCA profili 4-merow: czy naturalne promotory tworza archetypy?
kmery = [r["kmery"] for r in w03["rekordy"]]
alfabet = sorted({k for d in kmery for k in d})
X = np.array([[d.get(k, 0) for k in alfabet] for d in kmery], dtype=float)
X = X / X.sum(axis=1, keepdims=True)
Xc = X - X.mean(axis=0)
U, Sv, Vt = np.linalg.svd(Xc, full_matrices=False)
PC = U[:, :2] * Sv[:2]

# k-means w kilkunastu linijkach -- bez sklearn, repo zostaje bez zaleznosci
def kmeans(A, k=3, iteracji=60, ziarno=0):
    rng = np.random.default_rng(ziarno)
    C = A[rng.choice(len(A), k, replace=False)]
    for _ in range(iteracji):
        etyk = np.argmin(((A[:, None, :] - C[None]) ** 2).sum(-1), axis=1)
        nowe = np.array([A[etyk == i].mean(0) if (etyk == i).any() else C[i] for i in range(k)])
        if np.allclose(nowe, C):
            break
        C = nowe
    return etyk

etyk = kmeans(PC, k=3)
fig, ax = plt.subplots(figsize=(9, 7))
sns.scatterplot(x=PC[:, 0], y=PC[:, 1], hue=[f"archetyp {e+1}" for e in etyk],
                s=90, ax=ax)
for i, r in enumerate(w03["rekordy"]):
    if r["bije_dzikiego"]:
        ax.scatter(PC[i, 0], PC[i, 1], s=260, facecolors="none",
                   edgecolors="#e53e3e", lw=2.2, zorder=5)
war = (Sv[:2] ** 2 / (Sv ** 2).sum())
ax.set(title="E03 · PCA profili 4-merów — archetypy promotorów\n"
             "(czerwone obwódki = bije dzikiego u Sędziego)",
       xlabel=f"PC1 ({war[0]:.0%} wariancji)", ylabel=f"PC2 ({war[1]:.0%})")
plt.show()
print("Kazdy archetyp = jedna niezalezna hipoteza = jeden blok w portfelu E05.")
""")

    kod(r"""
if w03.get("chimery"):
    ch = pd.DataFrame(w03["chimery"])
    print(f"chimery bijace dzikiego: {int(ch['bije_dzikiego'].sum())}/{len(ch)}")
    fig, ax = plt.subplots(figsize=(10, 4.2))
    sns.barplot(data=ch, x="opis", y="bije_dzikiego", errorbar=None, ax=ax)
    ax.set(title="E03 · Chimery dziki × naturalny — odsetek bijących dzikiego",
           xlabel="miejsce cięcia", ylabel="odsetek")
    plt.show()
    print(ch[["etykieta", "opis", "dystans_od_dzikiego", "bije_dzikiego"]].to_string(index=False))
""")

# ── E04 ────────────────────────────────────────────────────────────────────
if jest("E04_blok_kombinacyjny"):
    md(r"""
---
# E04 · Plan faktorialny 2⁴

Cztery hipotezy działają na **rozłącznych** zbiorach pozycji, więc składają się
w jednej sekwencji:

| czynnik | pozycje |
|---|---|
| **A** dopasowanie gatunkowe | 154, 287, 362, 430, 434, 648, 750, 754, 778 |
| **B** rozbicie CreA | 560–565 |
| **C** zaprojektowany rdzeń | 783–800 |
| **D** tło z dekodera | pozostałe |

Plan zgłoszenia fazy 1 miał pięć bloków po jednej zmianie i **ani jednej
kombinacji**. Plan faktorialny daje efekty główne i interakcje z tej samej
liczby sekwencji — czyli odpowiedź na pytanie Jury „skąd wiecie, który
składnik działa".

Zmienna zależna: metryka z E01 (jeśli wariuje). To jest **proxy**, nie ocena
Wyroczni — trzy repliki na komórkę to eksploracja, nie test istotności.
""")

    kod(r"""
w04 = wczytaj("E04_blok_kombinacyjny")
kom = pd.DataFrame([{k: v for k, v in c.items() if k not in ("sekwencja", "rodzic", "metryki")}
                    | (c.get("metryki") or {}) for c in w04["komorki"]])
kom = kom.drop(columns=["pozycje_rekomendacji"], errors="ignore")
CZYN = [c for c in w04["czynniki"] if kom[c].nunique() > 1]

Y = next((y for y in ("blad_odtworzenia", "zmian_pod_gatunek", "srodek_masy")
          if y in kom and kom[y].nunique() > 1), None)
print(f"zmienna zalezna: {Y}   (nizej = lepiej dla obu metryk bledu)")
print(f"czynniki w planie: {CZYN}   komorek: {len(kom)}")
""")

    kod(r"""
if Y:
    fig, axs = plt.subplots(1, len(CZYN), figsize=(4.2 * len(CZYN), 4.4), squeeze=False)
    efekty = {}
    for ax, cz in zip(axs[0], CZYN):
        sns.pointplot(data=kom, x=cz, y=Y, ax=ax, errorbar="sd", capsize=0.15)
        sns.stripplot(data=kom, x=cz, y=Y, ax=ax, color="#718096", size=5, alpha=0.7)
        efekty[cz] = kom.loc[kom[cz] == 1, Y].mean() - kom.loc[kom[cz] == 0, Y].mean()
        ax.set(title=f"{cz}\nefekt główny = {efekty[cz]:+.2f}", xlabel="")
    fig.suptitle(f"E04 · Efekty główne (zmienna zależna: {Y})", fontweight="bold")
    plt.show()
    for k, v in sorted(efekty.items(), key=lambda x: x[1]):
        print(f"  {k:<14} {v:+7.2f}   {'POPRAWA' if v < 0 else 'pogorszenie'}")
""")

    kod(r"""
if Y and len(CZYN) > 1:
    Mi = pd.DataFrame(index=CZYN, columns=CZYN, dtype=float)
    for a in CZYN:
        for b in CZYN:
            if a == b:
                Mi.loc[a, b] = np.nan
                continue
            def sr(x, y):
                s = kom[(kom[a] == x) & (kom[b] == y)][Y]
                return s.mean() if len(s) else np.nan
            Mi.loc[a, b] = (sr(1, 1) - sr(1, 0)) - (sr(0, 1) - sr(0, 0))
    fig, ax = plt.subplots(figsize=(7, 5.6))
    sns.heatmap(Mi.astype(float), annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
    ax.set(title="E04 · Interakcje parowe\n(silna interakcja = ta kombinacja dostaje własny blok)")
    plt.show()
""")

    kod(r"""
if Y:
    sygn = kom[CZYN].astype(str).agg("".join, axis=1)
    kom = kom.assign(komorka=[
        "".join(f"{c[0]}{v}" for c, v in zip(CZYN, row)) for row in kom[CZYN].values])
    sr = kom.groupby("komorka", as_index=False)[Y].agg(["mean", "std", "count"]).reset_index()
    sr = sr.sort_values("mean")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=sr, x="komorka", y="mean", ax=ax, color="#2b6cb0")
    ax.errorbar(range(len(sr)), sr["mean"], yerr=sr["std"].fillna(0),
                fmt="none", ecolor="#1a202c", capsize=4)
    ax.set(title=f"E04 · Ranking komórek ({Y}, niżej = lepiej) — pierwsza od lewej wygrywa",
           xlabel="komórka planu", ylabel=Y)
    ax.tick_params(axis="x", rotation=60)
    plt.show()
    print(sr.to_string(index=False))
""")

    kod(r"""
if Y:
    fig, ax = plt.subplots(figsize=(9, 6))
    zgr = kom.groupby("komorka").agg(srednia=(Y, "mean"),
                                     wygrane=("bije_dzikiego", "mean")).reset_index()
    sns.scatterplot(data=zgr, x="srednia", y="wygrane", s=150, ax=ax)
    for _, r in zgr.iterrows():
        ax.annotate(r["komorka"], (r["srednia"], r["wygrane"]),
                    textcoords="offset points", xytext=(7, 5), fontsize=8)
    ax.set(title="E04 · Zgodność scorera z Sędzią — punkty odstające to rozjazd proxy",
           xlabel=f"{Y} (niżej = lepiej wg Nawigatora)",
           ylabel="odsetek wygranych u Sędziego")
    plt.show()
    print("Komorka z dobrym scorerem i przegrana u Sedziego to KANDYDATKA, nie odpad:")
    print("Sedzia nie widzi gatunku ani derepresji (W4, W7).")
""")

# ── E06 ────────────────────────────────────────────────────────────────────
if jest("E06_operator_krzyzowania"):
    md(r"""
---
# E06 · Operator krzyżowania — rekombinacja czy dziedziczenie?

Rozbicie wgranej puli na sposób powstania dało dwunastokrotną różnicę:
`nav_*` (surowe wyjścia `/edycje`) przechodzą bramkę Sędziego w **6 %**,
`hyb_*` (krzyżówki) w **72 %**. Tyle że rodzicami krzyżówek byli **zwycięzcy
turnieju**, więc efekt operatora jest pomieszany z preselekcją.

Rozstrzyga jedno ramię: **krzyżowanie dwóch przegranych**. Jeśli ich dzieci
wygrywają — działa operator. Jeśli nie — działała selekcja rodziców.
""")

    kod(r"""
w06 = wczytaj("E06_operator_krzyzowania")
r06 = pd.DataFrame([{k: v for k, v in r.items()
                     if k not in ("sekwencja", "rodzic_a", "rodzic_b", "metryki")}
                    for r in w06["rekordy"]])

ram = (r06.groupby("ramie")
       .agg(n=("bije_dzikiego", "size"), wygrane=("bije_dzikiego", "sum"),
            bije_rodzica=("bije_rodzic_a", "sum"),
            dystans=("dystans_rodzic_a", "median"))
       .reset_index())
ram["odsetek"] = ram["wygrane"] / ram["n"]
ram["rola"] = np.where(ram["ramie"].str.startswith(("R1", "R2")), "kontrola", "ramię testowe")
print(ram.to_string(index=False))
""")

    kod(r"""
fig, ax = plt.subplots(figsize=(10, 4.8))
BARWY = {"kontrola": "#d69e2e", "ramię testowe": "#2b6cb0"}
sns.barplot(data=ram.sort_values("odsetek"), y="ramie", x="odsetek", hue="rola",
            palette=BARWY, dodge=False, ax=ax, width=0.72)
for p, (_, r) in zip(ax.patches, ram.sort_values("odsetek").iterrows()):
    ax.text(r["odsetek"] + 0.015, p.get_y() + p.get_height() / 2,
            f"{r['wygrane']}/{r['n']}  ({r['odsetek']:.0%})",
            va="center", fontsize=10, color="#1a202c")
ax.set(title="E06 · Odsetek sekwencji przechodzących bramkę Sędziego",
       xlabel="odsetek bijących dzikiego", ylabel="", xlim=(0, 1.0))
ax.legend(title="", loc="lower right", frameon=False)
sns.despine(ax=ax)
plt.show()
""")

    md(r"""
**Jak to czytać.** Krzyżowanie **przegranych** siedzi na zerze — dokładnie tam,
gdzie surowy dekoder. Krzyżowanie **zwycięzców** i zwykła **mutacja zwycięzcy
o ten sam dystans** dają praktycznie to samo. Operator nie wnosi nic; wnosi
wyłącznie to, od kogo się zaczyna.
""")

    kod(r"""
bez_rodzica = int(r06["bije_rodzic_a"].sum())
wszystkich = int(r06["bije_rodzic_a"].notna().sum())
print(f'''
   +--------------------------------------------------------------+
   |  POTOMKOW BIJACYCH WLASNEGO RODZICA:  {bez_rodzica:>3} / {wszystkich:<3}                 |
   +--------------------------------------------------------------+

Wszystkie ramiona, wszystkie operatory. Nic nie przewyzsza swojego rodzica.
Znaczy to, ze jedyna droga w gore jest ZNALEZIENIE lepszego ziarna, a nie
przetwarzanie tego, ktore juz mamy. Stad E07.
''')
""")

# ── E07 ────────────────────────────────────────────────────────────────────
if jest("E07_przesiew"):
    md(r"""
---
# E07 · Przesiew — gdzie siedzą ziarna

Skoro potomek nie bije rodzica, to liczy się wyłącznie **ile niezależnych
ziaren** uda się znaleźć. Wgrane zgłoszenie ma 39 sekwencji przechodzących
bramkę, ale pochodzą one z **trzech** ziaren — a TOP10 jest statystyką
pozycyjną, więc widzi trzy losowania, nie trzydzieści dziewięć (W11).
""")

    kod(r"""
w07 = wczytaj("E07_przesiew")
skan = pd.DataFrame([{k: v for k, v in x.items() if k != "sekwencja"} for x in w07["skan"]])
ziarna = w07["ziarna"]
print(f"przesiano {len(skan)} sekwencji, ziaren {len(ziarna)} ({len(ziarna)/len(skan):.1%})")
print(f"niezaleznych skupien: {len(w07['skupienia'])} (prog {w07['prog_ziarna']} pz)")

bal = json.loads((TU / "E07_przesiew" / "wyniki_balans.json").read_text(encoding="utf-8"))
kom = pd.DataFrame(bal["komorki"])
kom["odsetek"] = kom["trafien"] / kom["n"]
# blad standardowy proporcji -- bez tego roznica 5 % vs 11 % wyglada na wynik
kom["se"] = np.sqrt(kom["odsetek"] * (1 - kom["odsetek"]) / kom["n"])
print("\nZBALANSOWANY test (rowne n na komorke):")
print(kom[["ile_kodow", "trafien", "n", "odsetek", "se"]].to_string(index=False))
""")

    kod(r"""
fig, ax = plt.subplots(figsize=(9, 4.6))
sns.barplot(data=kom, x="ile_kodow", y="odsetek", color="#2b6cb0", ax=ax, width=0.66)
ax.errorbar(range(len(kom)), kom["odsetek"], yerr=1.96 * kom["se"],
            fmt="none", ecolor="#1a202c", capsize=5, lw=1.6)
for i, r in kom.iterrows():
    ax.text(i, r["odsetek"] + 1.96 * r["se"] + 0.006, f"{r['trafien']}/{r['n']}",
            ha="center", fontsize=9.5, color="#1a202c")
ax.set(title="E07 · Odsetek trafień w bramkę wg ile_kodow (poziom 2, równe n)",
       xlabel="ile_kodow", ylabel="odsetek sekwencji bijących dzikiego")
sns.despine(ax=ax)
plt.show()

print('''
Tylko ile_kodow=4 jest martwe (0/96). Od 8 w gore wszystko lezy plasko
w granicach 5-11 %, a przedzialy 95 % zachodza na siebie -- czyli PARAMETR
NIE STERUJE TRAFIENIAMI. Steruje nimi liczba losowan.

To potwierdza W2 z fazy 1 na nowej osi: W2 mierzylo DYSTANS, tutaj mierzymy
ODSETEK TRAFIEN, i w obu wypadkach ile_kodow nie jest pokretlem.
''')
""")

    kod(r"""
# czy ziarna sa naprawde niezalezne: rozklad dystansow Hamminga parami
sz = [z["sekwencja"] for z in ziarna]
pary = np.array([S.hamming(sz[i], sz[j]) for i in range(len(sz)) for j in range(i + 1, len(sz))])

fig, axs = plt.subplots(1, 2, figsize=(13, 4.4))
sns.histplot(pary, bins=30, color="#2b6cb0", ax=axs[0])
axs[0].axvline(w07["prog_ziarna"], ls="--", lw=2, color="#e53e3e")
axs[0].text(w07["prog_ziarna"], axs[0].get_ylim()[1] * 0.94,
            f"  próg niezależności {w07['prog_ziarna']} pz", color="#c53030", fontsize=9.5)
axs[0].set(title="E07 · Dystanse Hamminga między ziarnami (wszystkie pary)",
           xlabel="dystans (pz)", ylabel="liczba par")

wyd = pd.DataFrame(w07["chmury"]).groupby("ziarno")["bije_dzikiego"].mean()
sns.histplot(wyd, bins=12, color="#38a169", ax=axs[1])
axs[1].axvline(wyd.mean(), ls="--", lw=2, color="#1a202c")
axs[1].text(wyd.mean(), axs[1].get_ylim()[1] * 0.94,
            f"  średnia {wyd.mean():.0%}", fontsize=9.5)
axs[1].set(title="E07 · Wydajność chmury wokół ziarna",
           xlabel="odsetek potomstwa utrzymującego wygraną", ylabel="liczba ziaren")
for a in axs:
    sns.despine(ax=a)
plt.show()

print(f"najmniejszy dystans miedzy ziarnami: {pary.min()} pz "
      f"(prog {w07['prog_ziarna']}) -- zadna para nie jest ta sama rodzina")
""")

# ── porownanie portfeli ────────────────────────────────────────────────────
if (TU / "E05_portfel" / "pomiar_portfela.json").exists():
    md(r"""
---
# Portfele — pomiar przed zgłoszeniem

Bramka Sędziego jest darmowa i powtarzalna, a okno `/wgraj` jest jedno na pięć
minut. Nie ma powodu, żeby o składzie pliku dowiadywać się z rankingu.
""")

    kod(r"""
pom = json.loads((TU / "E05_portfel" / "pomiar_portfela.json").read_text(encoding="utf-8"))
NAZWY = {"pula.fasta": "v1 — wgrane zgłoszenie", "v2.fasta": "v2 — plan 12 bloków",
         "v3.fasta": "v3 — przesiew (E07)"}
port = pd.DataFrame([{"portfel": NAZWY.get(Path(r["plik"]).name, Path(r["plik"]).name),
                      "n": r["n"], "przechodzi": r["przechodzi_bramke"],
                      "odsetek": r["przechodzi_bramke"] / r["n"]}
                     for r in pom["raporty"]]).sort_values("odsetek")

BARWY3 = ["#2b6cb0", "#d69e2e", "#38a169"]
fig, ax = plt.subplots(figsize=(10, 3.8))
sns.barplot(data=port, y="portfel", x="odsetek", ax=ax, width=0.62,
            hue="portfel", palette=BARWY3, legend=False)
for p, (_, r) in zip(ax.patches, port.iterrows()):
    ax.text(r["odsetek"] + 0.015, p.get_y() + p.get_height() / 2,
            f"{r['przechodzi']}/{r['n']}  ({r['odsetek']:.0%})",
            va="center", fontsize=10.5, color="#1a202c")
ax.set(title="Odsetek sekwencji przechodzących bramkę Sędziego",
       xlabel="", ylabel="", xlim=(0, 1.12))
ax.set_xticks([])
sns.despine(ax=ax, bottom=True)
plt.show()
print(port.to_string(index=False))
""")

    md(r"""
> **Zastrzeżenie, bez którego ten wykres wprowadza w błąd.** Bramka Sędziego
> mierzy *prototypowość*, nie siłę promotora (W4). Bloki 2–12 portfela v2
> przegrywają, bo zmieniają wymiary, których Sędzia z definicji nie widzi:
> gatunek, derepresję kataboliczną, kontekst genu. Zero na bramce **nie znaczy**,
> że są słabe — znaczy, że nie mamy na nie żadnego lokalnego dowodu.
> v3 optymalizuje jedyne proxy, jakie mamy, i tym samym jest najbardziej narażony
> na prawo Goodharta z sekcji 6 briefu.
""")


# ── podsumowanie ───────────────────────────────────────────────────────────
md(r"""
---
# Wnioski globalne

Ta sekcja jest po to, żeby nie trzeba było czytać czterech notebooków przed
zgłoszeniem. Pełny rejestr: [`WNIOSKI.md`](WNIOSKI.md).

## Co zmieniło się względem planu z fazy 1

| plan fazy 1 (komórka 36 `hipotezy.ipynb`) | co z nim robimy |
|---|---|
| 30 × dekoder + edycja rdzenia | **warunkowe na E02** — jeśli artefakt, budżet idzie na H7 i CreA |
| 30 × wariant gatunkowy | zostaje, to jedyna potwierdzona hipoteza (W7) |
| 20 × TATAAA w 720–770 | skurczone do 8 i zamienione na **skan** zamiast jittera (W11) |
| 10 × CreA | zostaje jako warstwa, nie osobny blok — jeśli E04 pokaże dodatni efekt B |
| 10 × zwycięzcy `hybryda` | zostaje jako trzon ALL100 |
| — | **NOWE: kombinacje.** Faza 1 nie miała ani jednej sekwencji łączącej dwie hipotezy, mimo że pozycje są rozłączne (W12) |
| — | **NOWE: 12 bloków zamiast 5.** TOP10 to statystyka pozycyjna — liczy się liczba niezależnych hipotez, nie sekwencji (W11) |
| — | **NOWE po E06/E07: 100 niezależnych ziaren.** Wgrane zgłoszenie ma 39 sekwencji przechodzących bramkę, ale pochodzą z **trzech** ziaren — czyli to trzy losowania, nie trzydzieści dziewięć (W22) |

## Jedno zdanie, jeśli nie ma czasu na resztę

**Cała optymalizacja rozstrzyga się na etapie losowania ziarna.** Ziarna
przechodzące bramkę Sędziego stanowią ~8 % wyjść dekodera, nic ich nie
przewyższa (1 przypadek na 494), a wszystko, co z nimi potem robimy —
krzyżowanie, mutacja, edycja rdzenia, dopasowanie gatunkowe — w najlepszym
razie **kopiuje ziarno z połowicznym powodzeniem**.

## Cztery rzeczy na prezentację — trzy z nich negatywne

Każda jest kontrolą, która unieważniła nasz własny wcześniejszy wniosek.
To jest mocniejszy materiał niż wynik pozytywny bez kontroli.

1. **E06 — kontrola, która obaliła nasz najlepszy wynik.** Mieliśmy 72 % vs 6 %
   i gotową opowieść o sile rekombinacji. Ramię „krzyżowanie dwóch przegranych"
   dało **0/16** — czyli tyle, co surowy dekoder. Ramię „mutacja o ten sam
   dystans" dało 50 %, czyli tyle, co krzyżowanie. Operator nie robi nic;
   wszystko robi preselekcja rodzica.
2. **E07 — kontrola, która obaliła nasz własny trend.** Niezbalansowany przesiew
   pokazywał ładną monotoniczność odsetka trafień po `ile_kodow`
   (7,1 % → 9,2 % → 11,2 %). Przy **równym n** trend znika: poza martwym
   `ile_kodow = 4` wszystko leży płasko w granicach 5–11 %. Pierwsza wersja
   próbkowała wyłącznie te komórki, które trafiły w rzadkiej siatce.
3. **W18 — konfundacja pochodzeniem.** `blad_odtworzenia` ma d Cohena = −0,48
   między grupami i **+0,06** wewnątrz jednorodnej puli. Ten sam skalar,
   ta sama zmienna zależna, przeciwny wniosek — zależnie od tego, czy próba
   jest zlepkiem, czy nie.
4. **E02 — kontrola negatywna architektury.** Szczyt `wagaP` nie drgnął przy
   rotacji treści o 100/200/400/600 pz: siedzi na krawędzi wejścia, nie na
   biologii. Sprawdzenie tego było warte więcej niż użycie sygnału.

## Uczciwe ograniczenia

- **Bramka Sędziego to nie jest miara siły promotora** (W4), tylko
  prototypowości. Portfel v3 maksymalizuje dokładnie to proxy i jest przez to
  najbardziej narażony na prawo Goodharta z sekcji 6 briefu. Jedyną przesłanką,
  że bramka koreluje z Wyrocznią, jest to, że pula o 39 % przejść dostała ALL100 #1.
- **Zero na bramce nie znaczy „słabe".** Bloki 2–12 portfela v2 zmieniają wymiary
  niewidoczne dla Sędziego (gatunek, derepresja, kontekst genu). Znaczy to
  „nie mamy na to lokalnego dowodu", a nie „to nie działa".
- Wszystkie zmienne zależne w tej fazie to **proxy z Nawigatora**. Jedynym
  prawdziwym sygnałem jest ranking po wgraniu, a on niesie ~1 bit na 5 minut
  przy pięciu drużynach.
- W planie faktorialnym repliki przy D=0 są **identyczne** (edycje A/B/C są
  deterministyczne), więc rozstęp replik dla połowy planu jest zerowy
  z konstrukcji, a nie z powtarzalności pomiaru.
- „Niezależność" ziaren to niezależność **sekwencyjna** (dystans Hamminga ≥ 40 pz),
  nie biologiczna. Dwa odległe ziarna mogą realizować ten sam mechanizm.
- Model nie był walidowany laboratoryjnie. Wynik to predykcja modelu, nie
  aktywność mokra.

## Następny krok

Portfele są zbudowane i **zmierzone lokalnie**; okno `/wgraj` nie zostało zużyte.

```bash
python -m hyppe waliduj runs/julian/v3.fasta
python -m hyppe me                              # zgloszenie_mozliwe_za_s
python -m hyppe wgraj  runs/julian/v3.fasta --dry-run
python -m hyppe wgraj  runs/julian/v3.fasta
```
""")


def main() -> int:
    nb = nbf.v4.new_notebook()
    nb.cells = [nbf.v4.new_markdown_cell(t) if typ == "md" else nbf.v4.new_code_cell(t)
                for typ, t in KOMORKI]
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}}
    WYJSCIE.write_text(nbf.writes(nb), encoding="utf-8")
    gotowe = [n for n in ("E01_funkcja_celu", "E02_artefakt_wagap",
                          "E03_naturalne_promotory", "E04_blok_kombinacyjny",
                          "E06_operator_krzyzowania", "E07_przesiew") if jest(n)]
    print(f"zapisano {WYJSCIE} ({len(nb.cells)} komorek)")
    print(f"sekcje z danymi: {', '.join(gotowe) if gotowe else 'BRAK -- uruchom run.py'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
