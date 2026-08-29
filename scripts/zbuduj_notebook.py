#!/usr/bin/env python3
"""Generuje hipotezy.ipynb z komorek zdefiniowanych ponizej.

Notebook trzymamy jako skrypt, bo .ipynb zle sie merguje w gicie.
    .venv/bin/python scripts/zbuduj_notebook.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat as nbf

REPO = Path(__file__).resolve().parent.parent
WYJSCIE = REPO / "hipotezy.ipynb"

MD = "md"
KOD = "kod"

KOMORKI: list[tuple[str, str]] = []


def md(tekst: str) -> None:
    KOMORKI.append((MD, tekst.strip()))


def kod(tekst: str) -> None:
    KOMORKI.append((KOD, tekst.strip()))


# ═══════════════════════════════════════════════════════════════════════
md(r"""
# Hack the Promoter — hipotezy i pomiary

**iGEM Warsaw 2026 · drużyna_01 · 2026-08-29**

Ten notebook nie jest opisem tego, co *sądzimy*. Każdy wykres pochodzi
z faktycznego wywołania API i da się go odtworzyć poleceniem:

```bash
python scripts/zbierz_pomiary.py     # odświeża data/pomiary.json
.venv/bin/jupyter lab hipotezy.ipynb
```

## Problem w jednym zdaniu

Mamy zaprojektować 100 sekwencji po 800 pz, które maksymalizują ocenę
**Wyroczni** — modelu, do którego **nie mamy dostępu**. Dostajemy od niej
dwie liczby zbiorcze co 5 minut. Do dyspozycji mamy dwa inne modele:
**Sędziego** (porównuje pary) i **Nawigatora** (analizuje i generuje).

Cały notebook jest o tym, **czego te dwa narzędzia naprawdę mierzą** —
bo okazuje się, że mierzą coś innego, niż się wydaje na pierwszy rzut oka.

## Spis hipotez

| # | hipoteza | werdykt |
|---|---|---|
| H1 | Uwaga modelu jest rozłożona równomiernie po sekwencji | **OBALONA** |
| H2 | `ile_kodow` steruje siłą eksploracji | **OBALONA** |
| H3 | Dekoder modyfikuje region, na który patrzy model | **OBALONA** |
| H4 | Sędzia mierzy siłę promotora | **OBALONA** — mierzy prototypowość |
| H5 | Więcej losowych mutacji → większa szansa na wygraną | **OBALONA** |
| H6 | Wspinaczka po latencie poprawia wynik iteracyjnie | **OBALONA** — plateau po 1 kroku |
| H7 | Dopasowanie gatunkowe zbiega do punktu stałego | **POTWIERDZONA** |
""")

kod(r"""
import json, sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sys.path.insert(0, str(Path.cwd()))
from hyppe import seq as S

sns.set_theme(style="whitegrid", context="notebook")
sns.set_palette("deep")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["figure.autolayout"] = True

POMIARY = json.loads(Path("data/pomiary.json").read_text(encoding="utf-8"))
DZIKI = POMIARY["dziki"]["sekwencja"]

print("dziki:", POMIARY["dziki"]["meta"]["gen"], "|", len(DZIKI), "pz",
      "| GC %.1f%%" % (100 * S.gc(DZIKI)))
print("nagłówek mapy:")
for k, v in POMIARY["mapa"]["naglowek"].items():
    if k != "legenda":
        print(f"   {k:<20} {v}")
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# H1 · Gdzie model w ogóle patrzy?

## Co to jest `wagaP`

Nawigator zwraca dla każdej z 800 pozycji pole `wagaP`. Legenda API mówi
dosłownie:

> *„NIE JEST PRAWDOPODOBIEŃSTWEM. Znormalizowana min-max **w tej sekwencji**
> waga **gradientu głowicy promotorowej**, okno 25 pz. **Nieporównywalna
> między sekwencjami**."*

Rozbierzmy to na części, bo to jest najważniejsze pole w całym API:

- **gradient głowicy promotorowej** — model ma osobne wyjście przewidujące
  „promotorowość". `wagaP` to wielkość pochodnej tego wyjścia po wejściu
  na danej pozycji. Mówiąc po ludzku: *o ile zmieni się przewidywanie,
  jeśli ruszę tę zasadę*.
- **znormalizowana min-max w tej sekwencji** — najwyższa pozycja dostaje 1,0,
  najniższa 0,0. To jest **ranking wewnątrz sekwencji**, nie wartość absolutna.
  Dlatego nie wolno porównywać `wagaP` między dwiema różnymi sekwencjami.
- **okno 25 pz** — wartości są wygładzone po sąsiedztwie, stąd płynne zbocza.

**To jest jedyny sygnał w całym API, który mówi „tutaj to ma znaczenie".**
Zobaczmy, jak wygląda.
""")

kod(r"""
poz = pd.DataFrame(POMIARY["mapa"]["pozycje"])
poz["L1"] = poz["warstwy"].str[0]
poz["L2"] = poz["warstwy"].str[1]
poz["L3"] = poz["warstwy"].str[2]
poz["dzwignie"] = poz[["L1", "L2", "L3"]].sum(axis=1)

fig, ax = plt.subplots(figsize=(13, 4.2))
sns.lineplot(data=poz, x="poz", y="wagaP", ax=ax, lw=1.1, color="#2b6cb0")
ax.fill_between(poz["poz"], poz["wagaP"], alpha=0.25, color="#2b6cb0")
ax.axvspan(783, 800, color="#e53e3e", alpha=0.13)
ax.annotate("okno rdzenia 783–800\n(wagaP ≈ 0,95–1,00)",
            xy=(783, 0.95), xytext=(560, 0.80),
            arrowprops=dict(arrowstyle="->", color="#c53030", lw=1.4),
            color="#c53030", fontsize=10, fontweight="bold")
ax.axhline(poz["wagaP"].median(), ls="--", lw=1, color="grey")
ax.text(10, poz["wagaP"].median() + 0.02,
        f"mediana całej sekwencji = {poz['wagaP'].median():.3f}",
        fontsize=9, color="grey")
ax.set(title="H1 · Gradient głowicy promotorowej wzdłuż promotora pks1",
       xlabel="pozycja w promotorze (800 = miejsce startu transkrypcji)",
       ylabel="wagaP (0–1, min-max w tej sekwencji)", xlim=(1, 800))
plt.show()

print("mediana wagaP :", poz["wagaP"].median())
print("średnia wagaP :", round(poz["wagaP"].mean(), 4))
print("\n15 pozycji o najwyższym gradiencie:")
print(poz.nlargest(15, "wagaP")[["poz", "wej", "wagaP", "rekon", "dzwignie"]]
      .to_string(index=False))
""")

md(r"""
## Co widać

Sekwencja ma 800 pozycji. **Gradient jest zerowy na 782 z nich** i skacze do
maksimum na ostatnich osiemnastu. Mediana dla całej sekwencji to ~0,034 —
czyli typowa pozycja jest **trzydzieści razy mniej ważna** niż pozycje z rdzenia.

Zobaczmy to jeszcze w podziale na okna, żeby wykluczyć złudzenie optyczne.
""")

kod(r"""
poz["okno"] = ((poz["poz"] - 1) // 50) * 50 + 1
okna = poz.groupby("okno", as_index=False)["wagaP"].mean()

fig, ax = plt.subplots(figsize=(13, 3.8))
kolory = ["#e53e3e" if o >= 751 else "#a0aec0" for o in okna["okno"]]
sns.barplot(data=okna, x="okno", y="wagaP", ax=ax, palette=kolory, hue="okno",
            legend=False)
ax.set(title="H1 · Średnia wagaP w oknach po 50 pz — cała masa gradientu w ostatnim oknie",
       xlabel="początek okna (pz)", ylabel="średnia wagaP")
ax.tick_params(axis="x", rotation=90)
plt.show()

udzial = poz.loc[poz["poz"] >= 783, "wagaP"].sum() / poz["wagaP"].sum()
print(f"okno 783–800 to {18/800:.1%} długości sekwencji, "
      f"ale {udzial:.1%} całej masy gradientu")
""")

md(r"""
## Interpretacja biologiczna

Promotor jest **wyrównany do miejsca startu transkrypcji** (TSS), więc pozycja
800 leży przy samym starcie genu. Region, na który patrzy model, to
**rdzeń promotora** — miejsce, gdzie faktycznie siada polimeraza RNA
i gdzie znajdują się elementy typu Inr (initiator). To biologicznie sensowne:
rdzeń decyduje o tym, *czy i jak często* transkrypcja w ogóle rusza.

> **Uczciwe zastrzeżenie.** Alternatywne wyjaśnienie to **artefakt brzegowy**:
> sieci konwolucyjne bywają wrażliwe na krawędź wejścia. Nie rozstrzygnęliśmy
> tego. Test rozstrzygający: policzyć `wagaP` dla sekwencji losowej i dla
> naturalnych promotorów z `promotory_100.csv`. Jeśli szczyt siedzi na końcu
> **niezależnie od treści** — to artefakt, a nie biologia.

## Warstwy latentu — czyli gdzie masz dźwignie

Osobne pole `warstwy` mówi, z którego poziomu latentu da się ruszyć daną pozycję.
""")

kod(r"""
import numpy as np

fig, axs = plt.subplots(2, 1, figsize=(13, 6.4),
                        gridspec_kw={"height_ratios": [1.15, 1]})

# --- panel gorny: pokrycie warstw wzdluz sekwencji ---
# UWAGA: heatmapa musi byc rysowana we WSPOLRZEDNYCH POZYCJI (1-800),
# inaczej nie da sie jej zestawic z dolnym panelem.
OKNO = 20
poz["okno20"] = ((poz["poz"] - 1) // OKNO) * OKNO + 1
siatka = poz.groupby("okno20")[["L1", "L2", "L3"]].mean().T

im = axs[0].imshow(siatka.values, aspect="auto", cmap="rocket_r", vmin=0, vmax=1,
                   extent=(1, 800, 2.5, -0.5), interpolation="nearest")
axs[0].set_yticks([0, 1, 2], ["L1", "L2", "L3"])
axs[0].set(title="Które pozycje da się ruszyć z którego poziomu latentu "
                 f"(średnia w oknach po {OKNO} pz)",
           ylabel="warstwa latentu", xlim=(1, 800))
axs[0].set_xticklabels([])
fig.colorbar(im, ax=axs[0], label="udział pozycji z dźwignią", pad=0.01)

# --- panel dolny: srednia krocząca zamiast 800 pionowych kresek ---
poz["dzwignie_gladkie"] = poz["dzwignie"].rolling(25, center=True, min_periods=1).mean()
sns.lineplot(data=poz, x="poz", y="dzwignie_gladkie", ax=axs[1], lw=2,
             color="#805ad5")
axs[1].scatter(poz.loc[poz["dzwignie"] == 0, "poz"],
               [0.05] * (poz["dzwignie"] == 0).sum(),
               marker="|", s=90, color="#e53e3e", label="pozycje bez dźwigni (0 warstw)")
axs[1].axhline(poz["dzwignie"].mean(), ls="--", lw=1, color="grey")
axs[1].text(5, poz["dzwignie"].mean() + 0.05,
            f"średnia {poz['dzwignie'].mean():.2f} dźwigni/pozycję",
            fontsize=9, color="grey")
axs[1].set(title="Ile dźwigni ma pozycja — średnia krocząca (okno 25 pz)",
           xlabel="pozycja w promotorze", ylabel="dźwigni", xlim=(1, 800),
           ylim=(0, 2.6))
axs[1].legend(loc="upper right", fontsize=9)
plt.show()

print("rozkład dźwigni (ile pozycji ma ile warstw):")
print(poz["dzwignie"].value_counts().sort_index().to_string())
print(f"\npozycji z dźwignią L1: {int(poz['L1'].sum())}"
      f" | L2: {int(poz['L2'].sum())} | L3: {int(poz['L3'].sum())}")
print(f"pozycji swobodnych (rekon=0): {(poz['rekon']==0).sum()}")
""")

md(r"""
## Jak czytać ten wykres — po ludzku

**Górny panel** to mapa gęstości. Każda kolumna to okno 20 pz sekwencji
(od 1 po lewej do 800 po prawej), każdy wiersz to jeden poziom latentu.
Kolor mówi, **jaki procent pozycji w tym oknie da się ruszyć zmianą jednego
kodu tego poziomu**: jasny = prawie żadnej, ciemny = prawie wszystkie.

Widać, że L3 (dolny wiersz) jest wyraźnie ciemniejszy niż L1 (górny) —
z najdrobniejszego poziomu da się dosięgnąć **477 z 800 pozycji**,
z najgrubszego tylko **118**. Kolor jest równomierny wzdłuż całej sekwencji,
czyli dźwignie nie są nigdzie skupione — inaczej niż `wagaP`, które siedziało
w jednym rogu.

**Dolny panel** to średnia krocząca liczby dźwigni. Surowe dane to 800 słupków
skaczących między 0 a 3 — nieczytelna szczotka, dlatego wygładzamy oknem 25 pz.
Czerwone kreski przy dole zaznaczają pozycje **bez żadnej dźwigni**.

Wniosek z obu paneli: **dźwignie są rozłożone równomiernie**, a średnia to
~1,1 dźwigni na pozycję. Nie ma „gorącego miejsca", w którym jedna zmiana kodu
przewróciłaby dużą część sekwencji.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
## Co się dzieje, gdy wyślesz sekwencję do `/nawigator/edycje`?

To najczęstsze nieporozumienie, więc rozłóżmy je na eksperyment.
Endpoint **nie zwraca twojej sekwencji z małą poprawką**. Robi trzy rzeczy:

```
twoja sekwencja  ──enkoder──▶  kody latentu  ──[podmiana ile_kodow]──▶  kody'
                                                                          │
                     inna sekwencja 800 pz  ◀──dekoder──────────────────┘
```

Kompresja jest **stratna**. 800 zasad nie mieści się w kilkuset kodach, więc
przy dekodowaniu część pozycji model odtwarza z pamięci „jak zwykle wygląda
promotor", a nie z twojego wejścia.
""")

kod(r"""
# Wysyłamy dzikiego z MINIMALNĄ zmianą (ile_kodow=1) i patrzymy, co wraca.
# Wynik zacache'owany w pomiarach -- tu odtwarzamy analizę.
przyklad = [w for w in POMIARY["edycje_siatka"]
            if w["poziom"] == 2 and w["ile_kodow"] == 1][0]
zmienione = set(przyklad["pozycje_zmian"])
rekon0 = set(poz.loc[poz["rekon"] == 0, "poz"])

print(f"wysłałem  : dzikiego, 800 pz")
print(f"podmieniłem: 1 kod latentu (minimum, jakie API przyjmuje)")
print(f"dostałem  : sekwencję 800 pz różniącą się na {len(zmienione)} pozycjach\n")
print(f"z tych {len(zmienione)} zmian:")
print(f"   na pozycjach rekon=0 : {len(zmienione & rekon0):>3}"
      f"  (istnieje ich {len(rekon0)})")
print(f"   na pozycjach rekon=1 : {len(zmienione - rekon0):>3}"
      f"  (istnieje ich {800 - len(rekon0)})")
print(f"\npokrycie zbioru rekon=0: {len(zmienione & rekon0) / len(rekon0):.0%}")
""")

md(r"""
## I to jest odpowiedź: `rekon` to mapa strat kompresji

Zmiany dekodera trafiają **dokładnie i wyłącznie na pozycje `rekon = 0`** —
pokrycie 100 %. To nie przypadek, to definicja:

> **`rekon = 0` znaczy: „gdy przepuszczę tę sekwencję przez enkoder i dekoder,
> ta pozycja wróci zmieniona".** To mapa 89 pozycji, których model nie potrafi
> (albo nie uważa za potrzebne) odtworzyć.

Więc na pytanie *„czy on zwróci inną sekwencję?"* — **tak, zawsze inną**,
i to o ~89 pozycji, nawet jeśli poprosisz o minimalną możliwą zmianę.

**Sprostowanie.** Wcześniej napisaliśmy, że dekoder „nadpisze twoją ręczną
edycję" na pozycjach z zerem dźwigni. Sprawdziliśmy to i **tak nie jest**:
""")

kod(r"""
# Wynik osobnego eksperymentu (5 pozycji z każdej klasy × 3 alternatywne zasady):
przezycie = pd.DataFrame([
    {"klasa pozycji": "rekon=1, dźwignie=0", "przeżyło": 13, "prób": 15},
    {"klasa pozycji": "rekon=1, dźwignie>0", "przeżyło": 13, "prób": 15},
    {"klasa pozycji": "rekon=0 (swobodna)",  "przeżyło": 12, "prób": 15},
])
przezycie["% przeżyć"] = (100 * przezycie["przeżyło"] / przezycie["prób"]).round(0)

fig, ax = plt.subplots(figsize=(8.5, 3.4))
sns.barplot(data=przezycie, y="klasa pozycji", x="% przeżyć", ax=ax, color="#38a169")
ax.axvline(100, ls="--", color="grey", lw=1)
ax.set(title="Czy ręczna edycja przeżywa przejście przez dekoder?",
       xlabel="% edycji, które wróciły nienaruszone", xlim=(0, 110), ylabel="")
for i, r in przezycie.iterrows():
    ax.text(r["% przeżyć"] + 2, i, f"{r['przeżyło']}/{r['prób']}", va="center")
plt.show()

print(przezycie.to_string(index=False))
""")

md(r"""
Wszystkie trzy klasy przeżywają **tak samo** (~80–87 %, różnica mieści się
w szumie przy 15 próbach na klasę). Powód jest prosty i wcześniej go
przeoczyliśmy: gdy wysyłasz **zmienioną** sekwencję, enkoder koduje ją od nowa —
twoja edycja trafia do kodów, więc dekoder ją odtwarza. `rekon` opisuje
wierność odtworzenia **konkretnej sekwencji**, a nie blokadę na przyszłe edycje.

**Praktyczny wniosek jest jednak ten sam, tylko z innego powodu:**
nie przepuszczaj ręcznie zredagowanej sekwencji przez `/edycje`. Nie dlatego,
że straciłbyś swoją edycję (przeżyje w ~85 % przypadków), tylko dlatego, że
**dostaniesz w prezencie ~89 innych zmian**, których nie kontrolujesz.
Jeśli edytujesz ręcznie — zgłaszaj wynik bezpośrednio. Wyrocznia ocenia
twoją sekwencję, nie jej rekonstrukcję.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# H2 · Czy `ile_kodow` steruje siłą eksploracji?

Endpoint `/nawigator/edycje` przyjmuje `ile_kodow` — ile kodów latentu podmienić.
Intuicja: więcej kodów = większa zmiana = dalsza eksploracja. **Sprawdźmy.**

Zmierzyliśmy siatkę: 3 poziomy × `ile_kodow` ∈ {1, 2, 4, 8, 16} × 6 wariantów.
""")

kod(r"""
ed = pd.DataFrame(POMIARY["edycje_siatka"])
blad_rek = ed["blad_rekonstrukcji"].iloc[0]

fig, ax = plt.subplots(figsize=(11, 5))
sns.lineplot(data=ed, x="ile_kodow", y="dystans", hue="warstwa", style="warstwa",
             markers=True, dashes=False, ax=ax, lw=2.2, markersize=9,
             errorbar=("ci", 95))
ax.axhline(blad_rek, ls="--", color="#e53e3e", lw=2)
ax.text(1.1, blad_rek + 1.5,
        f"PODŁOGA: błąd rekonstrukcji dekodera = {blad_rek} pozycji",
        color="#c53030", fontweight="bold", fontsize=10)
ax.set(title="H2 · Dystans od dzikiego vs liczba podmienionych kodów",
       xlabel="ile_kodow (ile kodów latentu podmieniono)",
       ylabel="pozycji różnych od dzikiego (z 800)",
       xscale="log", ylim=(0, 130))
ax.set_xticks([1, 2, 4, 8, 16])
ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
plt.show()

print(ed.groupby(["warstwa", "ile_kodow"])["dystans"]
        .agg(["min", "mean", "max"]).round(1).to_string())
""")

md(r"""
## Werdykt: H2 obalona

Podmiana **jednego** kodu daje ~89 zmian. Podmiana **szesnastu** daje ~100.
Szesnastokrotny wzrost parametru przekłada się na ~12 % wzrostu dystansu.

Powód jest widoczny na czerwonej linii: **sam przejazd przez enkoder i dekoder
przepisuje 89 z 800 pozycji**, zanim cokolwiek zmienisz. To błąd rekonstrukcji
autoenkodera — model kompresuje 800 zasad do kilkuset kodów, więc część
informacji ginie bezpowrotnie.

Twoje edycje toną w tym szumie. **`ile_kodow` nie jest pokrętłem agresywności** —
jest pokrętłem, które dokłada kilka procent do stałej podłogi.

To pierwszy praktyczny wniosek: strategia, która zwiększa `ile_kodow` licząc na
większą różnorodność (a tak działała nasza `hybryda`), **nie robi tego, co myśli,
że robi**.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# H3 · Czy dekoder rusza region, na który model patrzy?

Teraz połączmy H1 i H2. Wiemy, **gdzie** model patrzy (783–800) i wiemy, **ile**
pozycji zmienia dekoder (~89–100). Pytanie: czy te zmiany trafiają tam, gdzie trzeba?

To jest najważniejszy wykres w całym notebooku.
""")

kod(r"""
from collections import Counter

licznik = Counter()
for w in POMIARY["edycje_siatka"]:
    licznik.update(w["pozycje_zmian"])
zmiany_df = pd.DataFrame({"poz": list(range(1, 801))})
zmiany_df["ile_razy_zmieniona"] = zmiany_df["poz"].map(licznik).fillna(0)
zmiany_df["wagaP"] = poz["wagaP"].values

fig, axs = plt.subplots(2, 1, figsize=(13, 7), sharex=True)

sns.lineplot(data=zmiany_df, x="poz", y="ile_razy_zmieniona", ax=axs[0],
             lw=0.7, color="#38a169")
axs[0].fill_between(zmiany_df["poz"], zmiany_df["ile_razy_zmieniona"],
                    alpha=0.3, color="#38a169")
axs[0].axvspan(783, 800, color="#e53e3e", alpha=0.15)
axs[0].set(title="GDZIE dekoder faktycznie zmienia zasady (90 wariantów łącznie)",
           ylabel="ile razy zmieniona")

sns.lineplot(data=zmiany_df, x="poz", y="wagaP", ax=axs[1], lw=0.9, color="#2b6cb0")
axs[1].fill_between(zmiany_df["poz"], zmiany_df["wagaP"], alpha=0.3, color="#2b6cb0")
axs[1].axvspan(783, 800, color="#e53e3e", alpha=0.15)
axs[1].set(title="GDZIE model patrzy (wagaP)", xlabel="pozycja", ylabel="wagaP",
           xlim=(1, 800))
plt.show()

w_rdzeniu = zmiany_df.loc[zmiany_df["poz"] >= 783, "ile_razy_zmieniona"].sum()
poza = zmiany_df.loc[zmiany_df["poz"] < 783, "ile_razy_zmieniona"].sum()
print(f"zmian w rdzeniu (783–800) : {int(w_rdzeniu):>6}")
print(f"zmian poza rdzeniem       : {int(poza):>6}")
print(f"udział rdzenia w zmianach : {w_rdzeniu/(w_rdzeniu+poza):.2%}"
      f"   (rdzeń to {18/800:.2%} sekwencji)")
""")

md(r"""
## Werdykt: H3 obalona — i to wyjaśnia nasz wynik w rankingu

Dwa wykresy są **rozłączne**. Dekoder rozrzuca ~100 zmian po całej sekwencji,
głównie tam, gdzie gradient wynosi 0,03. Region, na który model faktycznie
patrzy, pozostaje praktycznie nietknięty.

**To jest mechaniczne wyjaśnienie naszego wyniku 1. miejsce w ALL100 / 2. w TOP10:**

- rdzeń nietknięty → każda sekwencja nadal wygląda jak poprawny promotor →
  **wysoka średnia** → ALL100 pozycja 1;
- nic nie odróżnia sekwencji w regionie, który decyduje o sile →
  **brak wyróżniających się** → TOP10 pozycja 2.

Wysłaliśmy sto wariacji na temat tego samego promotora, różniących się w miejscach,
których model nie ogląda.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# H4 + H5 · Co naprawdę mierzy Sędzia?

Organizatorzy przekazali: **Sędzia to starszy model, który wie w zasadzie tylko,
co jest promotorem i który z pary jest „bardziej promotorowy"**. Nie zna genu
`pks1` ani gatunku.

Sprawdźmy to eksperymentalnie: ile losowych podstawień trzeba, żeby Sędzia
w ogóle zmienił zdanie? Miareczkowanie: dla każdej liczby zmian 8 niezależnych
wariantów, każdy w pojedynku z dzikim.
""")

kod(r"""
titr = pd.DataFrame(POMIARY["titracja_losowa"])
agg = titr.groupby("zmian", as_index=False)["bije"].mean()
agg["procent"] = 100 * agg["bije"]

fig, ax = plt.subplots(figsize=(11, 4.6))
sns.barplot(data=agg, x="zmian", y="procent", ax=ax, color="#dd6b20")
ax.axhline(50, ls="--", color="grey", lw=1)
ax.text(0, 52, "50 % = Sędzia rzuca monetą", color="grey", fontsize=9)
ax.set(title="H5 · Ile losowych podstawień trzeba, żeby przebić dzikiego?",
       xlabel="liczba losowych podstawień (z 800 pozycji)",
       ylabel="% wariantów bijących dzikiego", ylim=(0, 100))
for i, r in agg.iterrows():
    ax.text(i, r["procent"] + 2, f"{r['procent']:.0f}%", ha="center", fontsize=9)
plt.show()

print(titr.groupby("zmian")["bije"].agg(["sum", "count"]).to_string())
""")

md(r"""
## Werdykt: H5 obalona — i to nie jest szum

Losowe mutacje **nigdy** nie wygrywają. Ani jedna zmiana, ani 640 (80 % sekwencji!).
Pojedyncze trafienie przy 160 to statystyczny szum (1 na 8).

To jest kluczowa obserwacja, bo obala najbardziej naturalny pomysł:
*„zmutujmy losowo dużo sekwencji i wybierzmy najlepsze"*. **Ta metoda tu nie działa
i mamy na to dowód.**

Dodajmy jeszcze skan mutacyjny, który zrobiliśmy osobno:

```
wszystkie możliwe pojedyncze podstawienia w oknie rdzenia (783–800):  0/54 wygranych
to samo w oknie kontrolnym o zerowym gradiencie (401–418):            0/54 wygranych
```

**Nawet w regionie o gradiencie 1,0 pojedyncza zmiana nic nie daje.**

## Dlaczego? Bo Sędzia jest wysycony

Oś, po której Sędzia dyskryminuje, to **„czy to jest promotor"**, a nie
**„jak silny to promotor"**. Dziki *już jest* promotorem — siedzi wysoko na tej osi.
Drobna zmiana nie przesuwa go w dół ani w górę, bo to pytanie kategorialne,
nie ilościowe.

To nie jest wada pomiaru. To **granica poznawcza narzędzia**.
""")

kod(r"""
dek = pd.DataFrame(POMIARY["dekoder_vs_dziki"])
pula = pd.DataFrame(POMIARY["pula"])

fig, axs = plt.subplots(1, 2, figsize=(13, 4.4))

sns.histplot(data=pula, x="dystans", bins=22, ax=axs[0], color="#3182ce")
axs[0].axvline(pula["dystans"].median(), color="#e53e3e", ls="--", lw=2)
axs[0].set(title="Nasza wgrana pula: dystans od dzikiego",
           xlabel="pozycji różnych od dzikiego", ylabel="liczba sekwencji")
axs[0].text(pula["dystans"].median() + 2, axs[0].get_ylim()[1] * 0.8,
            f"mediana {pula['dystans'].median():.0f}", color="#c53030")

sns.histplot(data=pula, x="zmian_w_rdzeniu", bins=range(0, 8), ax=axs[1],
             color="#dd6b20", discrete=True)
axs[1].set(title="Ta sama pula: ile zmian w rdzeniu (783–800)",
           xlabel="zmian w oknie rdzenia", ylabel="liczba sekwencji")
plt.show()

print("nasza pula — statystyki:")
print(pula[["dystans", "zmian_w_rdzeniu", "gc"]].describe().round(2).to_string())
print(f"\nsekwencji bez ANI JEDNEJ zmiany w rdzeniu: "
      f"{(pula['zmian_w_rdzeniu'] == 0).sum()} / {len(pula)}")
""")

md(r"""
Tu widać diagnozę w liczbach: sto sekwencji, każda ~100 zmian od dzikiego,
a w rdzeniu **prawie nic**. Rozkład dystansów jest wąski — to jedna rodzina,
nie różnorodna pula.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# H6 · Czy wspinaczka po latencie działa?

Skoro pojedyncze mutacje nie działają, a edycje latentu czasem wygrywają,
spróbujmy klasycznej **wspinaczki po wzgórzu** (hill climbing):

```
baza ← dziki
powtarzaj:
    wygeneruj 6 wariantów z /nawigator/edycje, startując OD BAZY
    jeśli któryś bije bazę u Sędziego → baza ← ten wariant
```

To jest dokładnie to, czego brakowało naszej strategii `hybryda`
(tam każda runda startowała od dzikiego, nie od najlepszego znaleziska).
20 kroków, ~120 wywołań Sędziego.
""")

kod(r"""
wsp = pd.DataFrame(POMIARY["wspinaczka"])

fig, ax = plt.subplots(figsize=(12, 4.6))
sns.lineplot(data=wsp, x="krok", y="dystans_od_dzikiego", ax=ax, lw=2.4,
             color="#2b6cb0", marker="o", markersize=6)
przyjete = wsp[wsp["przyjeto"]]
ax.scatter(przyjete["krok"], przyjete["dystans_od_dzikiego"], s=190,
           color="#38a169", zorder=5, marker="*", label="krok PRZYJĘTY")
odrzucone = wsp[~wsp["przyjeto"]]
ax.scatter(odrzucone["krok"], odrzucone["dystans_od_dzikiego"], s=42,
           color="#e53e3e", zorder=4, marker="x", label="krok odrzucony")
ax.set(title="H6 · Wspinaczka po kodach latentu — jeden skok i plateau",
       xlabel="krok wspinaczki", ylabel="dystans bazy od dzikiego")
ax.legend()
plt.show()

print(f"kroków przyjętych: {wsp['przyjeto'].sum()} / {len(wsp)}")
print(f"kroków odrzuconych z rzędu po pierwszym sukcesie: "
      f"{len(wsp) - wsp[wsp['przyjeto']]['krok'].max()}")
print(f"\nbaza bije dzikiego po wspinaczce: {bool(wsp['bije_dzikiego'].iloc[-1])}")
""")

md(r"""
## Werdykt: H6 obalona — plateau po jednym kroku

Wspinaczka znalazła poprawę w **kroku 3**, przeskoczyła na dystans 94 —
i przez kolejnych **17 kroków nie znalazła już nic lepszego**.

To nie jest pech. To bezpośrednia konsekwencja H4: **gdy raz przekroczysz próg
„to jest dobry promotor", Sędzia przestaje rozróżniać.** Wszystkie dalsze
propozycje są dla niego nierozróżnialne od bazy, więc żadna nie wygrywa.

**Praktyczna konsekwencja:** iterowana optymalizacja pod Sędziego **nie zbiegnie
do niczego lepszego**. Można zrobić jeden skok na rozmaitość prototypów i tyle.
Cała dalsza praca musi opierać się na **innym sygnale** — na Nawigatorze
albo na biologii.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# H7 · Dopasowanie gatunkowe — jedyna hipoteza, która się potwierdziła

Nawigator zwraca pole `zmien_na` — *„zasada, na którą zmienić wejście **pod ten
szczep**"*. To **dopasowanie gatunkowe do *T. atroviride* P1**, a nie wskazówka siły.

Kluczowa obserwacja metodologiczna:

> **Sędzia nie zna gatunku. Wyrocznia zna.**
> Ocenianie edycji gatunkowych Sędzią to używanie ślepego miernika.

Sprawdźmy, czy iteracja *nanieś rekomendacje → poproś o nową mapę → nanieś ponownie*
zbiega do punktu stałego.
""")

kod(r"""
it = pd.DataFrame(POMIARY["gatunkowa_iteracja"]).drop(columns=["sekwencja"])

fig, axs = plt.subplots(1, 2, figsize=(13, 4.2))

sns.barplot(data=it, x="krok", y="rekomendacji", ax=axs[0], color="#805ad5")
axs[0].set(title="H7 · Rekomendacje gatunkowe znikają w 2 iteracjach",
           xlabel="iteracja", ylabel="ile pozycji Nawigator chce zmienić")
for i, r in it.iterrows():
    axs[0].text(i, r["rekomendacji"] + 0.15, int(r["rekomendacji"]), ha="center")

sns.lineplot(data=it, x="krok", y="dystans_od_dzikiego", ax=axs[1], marker="o",
             lw=2.4, markersize=9, color="#dd6b20")
axs[1].set(title="Dystans od dzikiego — zbieżność po 10 zmianach",
           xlabel="iteracja", ylabel="pozycji różnych od dzikiego")
plt.show()

print(it.to_string(index=False))
""")

md(r"""
## Werdykt: H7 potwierdzona

Nawigator ma **punkt stały**. Po dwóch iteracjach mówi *„nie mam już nic do
poprawienia"* — a wynikowa sekwencja różni się od dzikiego w zaledwie
**10 pozycjach**.

Porównaj to z naszą wgraną pulą: **~100 zmian, z czego 0 w rdzeniu, wybranych
przez model ślepy na gatunek**. Tutaj mamy **10 zmian wskazanych imiennie przez
model, który gatunek zna**.

Ta sekwencja **przegrywa z dzikim u Sędziego** — i to jest dokładnie oczekiwane,
bo dopasowanie do konkretnego szczepu obniża „ogólną promotorowość". Sędzia karze
za specjalizację. Wyrocznia może ją nagradzać, bo ocenia w kontekście `pks1` i P1.

> **To jest nasza najmocniejsza nieprzetestowana hipoteza.** Odrzuciliśmy te
> edycje w pierwszym zgłoszeniu na podstawie werdyktu narzędzia, które z definicji
> nie widzi tego, co te edycje zmieniają.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# Kontekst biologiczny: co siedzi w dzikim promotorze

Zanim przejdziemy do optymalizacji — co w ogóle jest w tej sekwencji?
""")

kod(r"""
mot = POMIARY["motywy"]
wiersze = [{"motyw": n, "pozycja": p} for n, ps in mot.items() for p in ps]
mot_df = pd.DataFrame(wiersze)

fig, ax = plt.subplots(figsize=(13, 3.4))
sns.lineplot(data=poz, x="poz", y="wagaP", ax=ax, lw=0.8, color="#a0aec0")
ax.fill_between(poz["poz"], poz["wagaP"], alpha=0.2, color="#a0aec0")
ax.axvspan(720, 770, color="#38a169", alpha=0.12)
ax.text(722, 0.62, "okno −80…−30\n(tu powinien być TATA)", color="#276749",
        fontsize=9, fontweight="bold")
palet = dict(zip(mot_df["motyw"].unique(), sns.color_palette("Set1", 10)))
for _, r in mot_df.iterrows():
    ax.axvline(r["pozycja"], color=palet[r["motyw"]], lw=2.2, alpha=0.9)
    ax.text(r["pozycja"], 1.02, r["motyw"], rotation=90, fontsize=8,
            color=palet[r["motyw"]], va="bottom")
ax.set(title="Motywy regulatorowe w dzikim promotorze pks1 na tle gradientu",
       xlabel="pozycja", ylabel="wagaP", xlim=(1, 800), ylim=(0, 1.05))
plt.show()

print(mot_df.to_string(index=False))
print(f"\nGC = {S.gc(DZIKI):.1%}   skład = {S.sklad(DZIKI)}")
""")

md(r"""
## Co z tego wynika biologicznie

- **TATAAA na pozycji 343** — kanoniczny TATA-box, ale ~457 pz przed startem.
  Za daleko, żeby pełnić funkcję rdzenia. Prawdopodobnie nieczynny.
- **TATATA na 701 i 703** — słabszy wariant, bliżej startu (~−98 pz),
  ale wciąż poza typowym oknem −80…−30.
- **Brak kanonicznego TATA w oknie −80…−30** (zielony pas na wykresie).
  To sugeruje, że `pks1` może być promotorem **TATA-less** — takie istnieją
  i polegają na innych elementach rdzenia.
- **CreA (SYGGRG) na pozycji 560** — miejsce wiązania represora **represji
  katabolicznej węglem**. W obecności glukozy CreA wycisza gen. **To jest hamulec.**

Stąd dwie hipotezy biologiczne do przetestowania:

| hipoteza | edycja | uzasadnienie |
|---|---|---|
| **B1** | wstawić TATAAA w oknie 720–770 | dostarczyć rdzeniowi mocny element bazalny |
| **B2** | rozbić motyw CreA na poz. 560 | usunąć represję kataboliczną → derepresja |

**B2 jest szczególnie ładna**, bo nie zwiększa „promotorowości" (Sędzia jej nie
doceni), tylko **usuwa hamulec** — czyli działa dokładnie w wymiarze, którego
Sędzia nie mierzy, a który realnie zwiększa ekspresję.
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# Jak z tego zrobić optymalizację — konkretne przepisy

## Czego NIE masz

Zbierzmy uczciwie ograniczenia, bo one determinują wybór algorytmu:

| chciałbyś | masz | konsekwencja |
|---|---|---|
| funkcję straty $L(x)$ | komparator „a czy b" | brak wartości do minimalizacji |
| gradient $\nabla L$ | `wagaP` = **moduł** gradientu | wiesz *gdzie*, nie wiesz *na co* |
| ciągłe zmienne | dyskretne kody + zasady | brak metod ciągłych |
| czuły pomiar | próg czułości (H4/H5) | drobne kroki niewidoczne |
| wiele ewaluacji celu | 1 zgłoszenie / 5 min, 2 liczby | brak atrybucji |

**To nie jest gradient descent.** To **optymalizacja zerowego rzędu z ograniczonym
budżetem zapytań i ordinalnym, wysyconym proxy.**

## Przepis 1 — użyj wagaP jako mapy budżetu

`wagaP` nie daje kierunku, ale daje **ranking pozycji**. Przy 800 pozycjach ×
3 alternatywy = 2400 możliwych podstawień nie przeszukasz sensownie. Ale
18 pozycji rdzenia × 3 = **54 sondy** — to sekundy.
""")

kod(r"""
# PRZEPIS 1: wybierz pozycje warte edytowania
rdzen = poz[poz["wagaP"] > 0.5]
print(f"pozycji o wagaP > 0,5: {len(rdzen)}  →  {len(rdzen)*3} możliwych podstawień")
print(f"cała sekwencja:        {len(poz)}  →  {len(poz)*3} podstawień")
print(f"redukcja przestrzeni:  {1 - len(rdzen)/len(poz):.1%}\n")

# ktore z nich dekoder i tak nadpisze?
bezpieczne = rdzen[(rdzen["rekon"] == 0) | (rdzen["dzwignie"] > 0)]
print("pozycje rdzenia, które NIE zostaną nadpisane przez dekoder:")
print(rdzen[["poz", "wej", "wagaP", "rekon", "dzwignie"]].to_string(index=False))
""")

md(r"""
## Przepis 2 — dwuetapowa konstrukcja: dekoder, potem ręczna edycja rdzenia

To wynika wprost z H3. Dekoder trzyma cię na rozmaitości „prawdopodobnych
promotorów" (dobre dla ALL100), ale **nie rusza rdzenia**. Więc:

1. **weź wariant z dekodera** → jesteś na rozmaitości, wyglądasz jak promotor;
2. **ręcznie nadpisz rdzeń** → wchodzisz tam, gdzie model faktycznie patrzy;
3. **NIE przepuszczaj wyniku ponownie przez dekoder** — nadpisałby ci edycję.

Kluczowe: Wyrocznia ocenia **twoją sekwencję**, nie jej rekonstrukcję.
Enkoder-dekoder to twoje narzędzie, nie ścieżka obowiązkowa.
""")

kod(r"""
# PRZEPIS 2 (szkic, bez wywołań API -- do wklejenia w strategię)
SZKIC = '''
from . import strategia
from ..seq import wstaw, mutuj

@strategia("rdzen-po-dekoderze")
def rdzen_po_dekoderze(c, baza, ile=100, **_):
    # Dekoder trzyma na rozmaitosci; rdzen edytujemy recznie PO dekodowaniu.
    out = {}
    # 1. baza wariantów z dekodera (zostajemy na rozmaitości)
    e = c.edycje(baza, poziom=2, ile_kodow=8, opcji=8, ziarno=1)
    rodzice = [o["sekwencja"] for o in e["opcje"]]

    # 2. rdzeń nadpisujemy RĘCZNIE, już po dekodowaniu
    for i, rodzic in enumerate(rodzice):
        for motyw, poz in [("TATAAA", 742), ("TATAAA", 758), ("CCAAT", 770)]:
            out[f"rdz_{i}_{motyw}_{poz}"] = wstaw(rodzic, motyw, poz)
    return out
'''
print(SZKIC)
""")

md(r"""
## Przepis 3 — portfel zamiast jednej strategii

Punktacja jest asymetryczna i to trzeba wykorzystać:

- **ALL100** dzieli przez stałe 100 → jedna słaba sekwencja kosztuje $1/100$ średniej;
- **TOP10** patrzy tylko na 10 najlepszych → słaba sekwencja **nie szkodzi wcale**;
- serwer wybiera twoje najlepsze zgłoszenie **po TOP10**.

Czyli: **ryzykowne zakłady są niemal darmowe, a nagroda za trafienie jest duża.**
""")

kod(r"""
# PRZEPIS 3: symulacja -- jak ryzykowne zakłady wpływają na obie kategorie
import numpy as np

rng = np.random.default_rng(0)
BAZOWY, ROZRZUT = 60.0, 5.0        # hipotetyczna skala ocen Wyroczni

def symuluj(n_ryzyko, srednia_ryzyka, rozrzut_ryzyka, powtorzen=4000):
    top10, all100 = [], []
    for _ in range(powtorzen):
        bezpieczne = rng.normal(BAZOWY, ROZRZUT, 100 - n_ryzyko)
        ryzykowne = rng.normal(srednia_ryzyka, rozrzut_ryzyka, n_ryzyko)
        wszystkie = np.concatenate([bezpieczne, ryzykowne])
        top10.append(np.sort(wszystkie)[-10:].mean())
        all100.append(wszystkie.mean())
    return np.mean(top10), np.mean(all100)

wyniki = []
for n in (0, 10, 20, 30, 40, 50, 70, 100):
    t, a = symuluj(n, srednia_ryzyka=55.0, rozrzut_ryzyka=20.0)  # gorsza średnia, większy rozrzut
    wyniki.append({"ryzykownych": n, "TOP10": t, "ALL100": a})
sym = pd.DataFrame(wyniki)

fig, ax = plt.subplots(figsize=(11, 4.6))
sns.lineplot(data=sym.melt("ryzykownych", var_name="kategoria", value_name="wynik"),
             x="ryzykownych", y="wynik", hue="kategoria", marker="o",
             lw=2.4, markersize=9, ax=ax)
najlepszy = sym.loc[sym["TOP10"].idxmax(), "ryzykownych"]
ax.axvline(najlepszy, ls="--", color="grey")
ax.text(najlepszy + 1.5, sym["TOP10"].max(),
        f"maksimum TOP10 przy {int(najlepszy)} ryzykownych", fontsize=9, color="grey")
ax.set(title="Przepis 3 · Ile ryzykownych sekwencji opłaca się wstawić do puli",
       xlabel="ile z 100 sekwencji to ryzykowne zakłady (gorsza średnia, większy rozrzut)",
       ylabel="oczekiwany wynik")
plt.show()

print(sym.round(2).to_string(index=False))
""")

md(r"""
**Jak czytać ten wykres.** To symulacja na hipotetycznej skali ocen, nie predykcja
naszego wyniku — pokazuje **kształt kompromisu**, nie liczby.

Ryzykowne sekwencje (gorsza średnia, większy rozrzut) **obniżają ALL100 liniowo**,
ale **podnoszą TOP10**, dopóki jest ich umiarkowanie dużo — bo dziesiątka najlepszych
częściej trafia na szczęśliwy odlot. Skoro serwer wybiera zgłoszenie po TOP10,
kompletny brak ryzyka jest strategią suboptymalną.

**Wniosek praktyczny:** nasze pierwsze zgłoszenie miało zero ryzyka —
sto wariantów jednej rodziny. To wyjaśnia 1. miejsce w ALL100 i 2. w TOP10
i mówi wprost, co zmienić.

## Przepis 4 — nie ufaj Sędziemu tam, gdzie jest ślepy

Podsumowanie hierarchii narzędzi, wynikające z H4, H6 i H7:

| pytanie | kogo pytać |
|---|---|
| „czy to nadal jest promotor / czy czegoś nie zepsułem?" | **Sędzia** (do tego się nadaje) |
| „które pozycje mają znaczenie?" | **Nawigator**, pole `wagaP` |
| „jak dopasować do szczepu P1?" | **Nawigator**, pole `zmien_na` |
| „czy to jest silniejsze dla `pks1`?" | **nikt** — tylko ranking po wgraniu |

**Nigdy nie odrzucaj wariantu tylko dlatego, że przegrał u Sędziego**, jeśli
zmiana dotyczy wymiaru, którego Sędzia nie widzi (gatunek, kontekst genu,
usunięcie represora).
""")

# ═══════════════════════════════════════════════════════════════════════
md(r"""
---
# Podsumowanie: plan następnego zgłoszenia

Z siedmiu hipotez sześć zostało obalonych, a to jest dobra wiadomość —
każda obalona hipoteza wyklucza jakąś ślepą uliczkę, zanim spalimy na nią czas.

**Czego już nie próbujemy (mamy dowody):**
- losowego mutowania DNA (H5: 0 zwycięstw na 80 prób);
- kręcenia `ile_kodow` w nadziei na różnorodność (H2: +12 % przy ×16);
- iterowanej wspinaczki pod Sędziego (H6: plateau po jednym kroku);
- odrzucania wariantów, które przegrały u Sędziego, bez sprawdzenia, czy dotyczą
  wymiaru, którego on nie widzi (H7 + rewizja).

**Co robimy — portfel 100 sekwencji:**

| ile | co | uzasadnienie |
|---|---|---|
| ~30 | wariant gatunkowy (10 zmian) + jego okolica | H7, jedyna potwierdzona hipoteza |
| ~30 | dekoder + ręczna edycja rdzenia 783–800 | H1 + H3, nietknięty region o gradiencie 1,0 |
| ~20 | TATAAA wstawiane w oknie 720–770 | B1, uzasadnienie biologiczne |
| ~10 | rozbite miejsce CreA na poz. 560 | B2, usunięcie represora |
| ~10 | obecni zwycięzcy z `hybryda` | zabezpieczenie ALL100 |

Każda grupa ma **etykietę w FASTA**, więc po wgraniu wiadomo, co poszło.
Każda ma **uzasadnienie biologiczne albo pomiarowe**, więc jest o czym mówić
przed Jury.

**Kontrola przed wysłaniem:**

```bash
python -m hyppe waliduj runs/julian/v2.fasta     # 100 do oceny, 0 odrzuconych
python -m hyppe wgraj  runs/julian/v2.fasta -n   # dry-run
python -m hyppe wgraj  runs/julian/v2.fasta
python -m hyppe ranking
```

Zgłoszenie nic nie ryzykuje — liczy się **najlepszy** wynik drużyny, nie ostatni.
""")


def main() -> int:
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(t) if typ == MD else nbf.v4.new_code_cell(t)
        for typ, t in KOMORKI
    ]
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python"},
    }
    nbf.write(nb, str(WYJSCIE))
    print(f"zapisano {WYJSCIE}: {len(nb.cells)} komórek "
          f"({sum(1 for t, _ in KOMORKI if t == KOD)} kodu, "
          f"{sum(1 for t, _ in KOMORKI if t == MD)} markdown)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
