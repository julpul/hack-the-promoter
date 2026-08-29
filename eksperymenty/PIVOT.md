# PIVOT — od perturbacji do kompozycji

**Stan:** poz. 5/10, TOP10 6,0 (ranga 5), ALL100 7,0 (ranga 4), razem 13,0.
Utrzymywane zgłoszenie z **14:41**. Wszystko, co zrobiliśmy po tej godzinie
(v4 = 100 ziaren, v5 gatunkowy, v6 naturalny, v7 Goodhart, v8 CCAAT) **nie
pobiło własnego TOP10**. To nie jest pech — to jest wynik pomiarowy.

Czołówka: 02 (18,0), 07 (18,0), 05 (17,0). Dzielą nas 3–4 rangi w TOP10.

---

## 1. Co wiemy — trzy zdania

1. **Wszystkie trzy narzędzia są ślepe na cel.** Sędzia mierzy prototypowość
   dekodera i nigdy nie stawia niczego nad dzikim (0/100 naturalnych, 0/80
   losowych, plateau po 1 kroku). `wagaP` to artefakt brzegowy (100/101 sekwencji
   ma szczyt na poz. 788 niezależnie od treści). `blad_odtworzenia` to detektor
   pochodzenia, nie jakości (dekoder 16–27, prawdziwe DNA 63–95, rozkłady rozłączne).
2. **Sufit metody jest zmierzony.** 3 → 56 → 100 niezależnych ziaren dekodera:
   TOP10 nie drgnął od v3. Rozkład, z którego losujemy, ma sufit i jesteśmy przy nim.
3. **Cała nasza eksploracja to jedna okolica.** 100 „niezależnych ziaren" to
   100 rzutów dekodera z **tego samego** dzikiego, każde ~100 zmian od niego.
   W przestrzeni 800-wymiarowej to jeden punkt z chmurką, nie sto punktów.

**Diagnoza:** nie mamy problemu z próbkowaniem. Mamy problem z **punktem startowym
i z tym, że nigdy niczego nie zaprojektowaliśmy** — tylko perturbowaliśmy.

---

## 2. Korekta: „na końcu jest największy gradient" — to jest właśnie ten artefakt

`wagaP` rośnie na końcu **dla każdej sekwencji, jaką mu podamy**: dla rotacji
o 100/200/400/600 pz (treść przesunięta, szczyt został), dla permutacji, dla
sekwencji losowej, dla poli-A w rdzeniu. 100 na 101. To pochodna głowicy
siedzącej na sieci splotowej, a splot na krawędzi wejścia ma mniej sąsiadów.
**Budowanie strategii na tym gradiencie to powtórzenie błędu, który sami
obaliliśmy w E02.**

Ale intuicja „koniec jest ważny" jest **słuszna z innego powodu**. Informacja
pozycyjna w stu naturalnych promotorach wyrównanych do TSS:

```
poz.   1-700    0,019-0,030 bit    tło
poz. 751-800    0,055              2,6 × tło
poz. 798 (TSS-2)  IC 0,525  ->  A w 62/100    25 × tło
```

Rdzeń istnieje i jest w ostatnich ~50 pz — ale wyszedł z **konserwacji między
gatunkami**, nie z modelu.

**I tu jest pointa: rdzeń dzikiego `pks1` jest już normalny.** Log-odds wobec
PWM ze stu naturalnych: dziki 3,67 przy medianie 2,97 → **percentyl 52 %**
(kontrola w losowym oknie: 25 %). Nie ma tam czego naprawiać. Dźwignia leży
**powyżej** rdzenia.

---

## 3. Co mówi literatura — i co z tego mamy w danych

Przeszukanie literatury o inżynierii promotorów u grzybów strzępkowych daje
zbieżny obraz, i — co ważne — **każdy z tych elementów da się policzyć w naszych
stu naturalnych promotorach**.

### 3.1 Największe udokumentowane wzrosty pochodzą z wymiany miejsc cis

Promotor `cbh1` *T. reesei* zmodyfikowano zamieniając **osiem miejsc represora
ACE1** na miejsca aktywatorów **ACE2, Hap2/3/5 i Xyr1**. Warianty `cbh1pX`
(Xyr1) i `cbh1pA` (ACE2) dały **5,0 ×** i **3,6 ×** więcej wydzielanej mannanazy.
Inna praca na tym samym promotorze: **5,5 × / 7,4 ×** wzrost GFP.

To jest rząd wielkości, którego nie da się osiągnąć przesuwaniem pojedynczych
zasad — i dokładnie dlatego nasze perturbacje mają sufit.

### 3.2 Konfiguracja bije liczbę kopii

Kluczowa praca o układzie elementów cis w *T. reesei*: **konfiguracja elementów
ma większy wpływ na siłę promotora niż sama liczba miejsc wiązania**, a odległość
elementu od miejsca startu transkrypcji też jest istotna. Konkretnie:
**odwrócony powtórzony układ miejsc Xyr1 (XBS)** silnie podnosi aktywność `cbh1`.

W promotorze `xyn1` wyfootprintowano dokładny element:
`GGCTAAATGCGACATCTTAGCC` — odwrócony powtórzony `GGCTAA` rozdzielony 10 pz.

### 3.3 Architektura nukleosomowa: trakty poli(dA:dT)

Aktywność wariantów promotora koreluje z przewidywaną architekturą nukleosomową,
sterowaną przez **trakty poli(dA:dT)**. W *Pichia pastoris* manipulacja tymi
traktami w `AOX1` dała bibliotekę o aktywności **0,25 – 3,5 ×** dzikiego.
U *A. niger* siłę promotorów syntetycznych stroi się **tandemowym składaniem
elementów UAS** powyżej rdzenia.

### 3.4 Nasze dane: dziki `pks1` nie ma dwóch z tych elementów

Skan obu nici, dziki vs 100 naturalnych *Trichoderma*:

| element | rola | dziki | mediana nat. | % nat. z ≥1 | percentyl dzikiego |
|---|---|---|---|---|---|
| **CCAAT** (Hap2/3/5, CBC) | aktywator ogólny | **0** | 2 | 81 % | **0 %** |
| **GGCTAA** (Xyr1/ACE2, rdzeń XBS) | aktywator | **0** | 0 | 26 % | **0 %** |
| GGCWWW (XBS szeroki) | aktywator | 3 | 3 | 92 % | 39 % |
| SYGGRG (Cre1/CreA) | **represor** | 2 | 2 | 92 % | 40 % |
| trakt A/T ≥ 8 pz | NDR | 3 | 5 | 80 % | 42 % |

Dwa zera przy percentylu 0 %. Do tego **żaden ze stu naturalnych promotorów nie
ma odwróconego powtórzenia GGCTAA** — czyli element, który w literaturze daje
największy skok, jest **czysto inżynierski**, a nie kopiowany z natury. To jest
projekt, nie plagiat, i tak się go broni przed Jury.

---

## 4. Pivot: składamy promotor z części zamiast perturbować dziki

Przestajemy pytać „jak przesunąć dzikiego". Zaczynamy budować z bloków
o znanej funkcji, na **prawdziwym** podkładzie DNA.

```
-800 .............................................................. 0 (TSS)
|<-- podkład: prawdziwy promotor Trichoderma (jeden ze 100) -------->|
        [Cre1 rozbite]   [XBS array]  [CCAAT ×N]  [poli dA:dT]  [rdzeń]
                          -450..-330   -290..-170   -130..-105   -50..0
```

| blok | pozycja | treść | źródło |
|---|---|---|---|
| **rdzeń** | −50…0 | **nietknięty z podkładu** | E10: rdzeń dzikiego jest w normie, nie psujemy |
| **NDR** | −130…−105 | trakt poli(dA:dT), 20–26 pz | poli(dA:dT) → architektura nukleosomowa (AOX1: 0,25–3,5 ×) |
| **CCAAT** | −290, −250, −210, −170 | Hap2/3/5 | 81 % rodzaju ma, dziki 0; jeden z aktywatorów użytych w `cbh1` |
| **XBS** | −450…−330 | `GGCTAAATGCGACATCTTAGCC` (odwrócony powtórzony) ×2 albo tandem GGCTAA ×4 | element z `xyn1`; konfiguracja > liczba kopii |
| **Cre1** | wszędzie | **rozbite** (SYGGRG → 1 podstawienie) | wymiana miejsc represora to rdzeń metody z `cbh1` |
| **podkład** | reszta | prawdziwy promotor *Trichoderma* | `blad_odtworzenia` wraca w zakres naturalny 63–95 |

### Dlaczego to jest inna przestrzeń, a nie większa próba z tej samej

- **Podkład**: 100 prawdziwych promotorów zamiast jednego dzikiego → dystanse
  rzędu 600 pz między kandydatami, nie 100.
- **`blad_odtworzenia`** wraca do 63–95 zamiast 16–27 — jeśli Wyrocznia była
  trenowana na prawdziwych promotorach, wychodzimy z poza-rozkładu.
- **Każda zmiana ma nazwę białka**, więc W5 („losowe mutacje nie działają")
  nie jest kontrargumentem: to nie są losowe podstawienia, to instalacja miejsc
  wiązania w pozycjach wziętych z literatury i z rozkładu naturalnego.

### Przestrzeń wariantów (bez kombinatoryki na ślepo)

```
podkład      100 prawdziwych promotorów
XBS          {0, tandem×4, IR×1, IR×2}          4 warianty  <- konfiguracja, wg literatury najważniejsza
CCAAT        {0, 2, 4}                          3
NDR          {brak, 20 pz, 26 pz}               3
Cre1         {zostaw, rozbij}                   2
```

Nie mnożymy tego na ślepo. Bierzemy **plan czynnikowy**: 100 podkładów × jeden
pełny wariant „wszystko włączone" daje 100 sekwencji z maksymalną
różnorodnością podkładu. Osobne zgłoszenie testuje pojedyncze czynniki
(XBS włączony/wyłączony przy reszcie stałej) — to jest atrybucja przez ranking,
jedyna dostępna.

---

## 5. Trzy zgłoszenia, trzy pytania

Wgrania są darmowe (liczy się najlepsze, okno 5 min), więc każde jest pomiarem.

| # | plik | co zmienia | pytanie |
|---|---|---|---|
| **v9** | `v9_kompozyt.fasta` | 100 prawdziwych podkładów + pełny zestaw bloków | czy kompozycja bije perturbację? |
| **v10** | `v10_bez_xbs.fasta` | to samo **bez** XBS | ile daje sam element Xyr1? |
| **v11** | `v11_dziki_podklad.fasta` | te same bloki, ale podkład = dziki `pks1` | czy zysk pochodzi z bloków, czy z podkładu? |

v9 vs v11 rozdziela **podkład** od **projektu** — to jest kontrola, której
w całym projekcie jeszcze nie mieliśmy.

---

## 6. Co z Sędzią do losowania par

Ostrożnie. Sędzia ma zmierzone własności: powtarzalny (W16), ale **wysycony** —
0/100 prawdziwych promotorów i 0/15 chimer nad dzikim. Turniej par w takiej
przestrzeni nie ma czego rozdzielać, bo funkcja jest prawie stała.

Sensowne użycie: **bramka na wejściu do puli** („czy to nadal jest promotor")
i **jeden pomiar diagnostyczny** — czy w rodzinie kompozytów Sędzia w ogóle
produkuje wariancję. Jeśli produkuje, turniej szwajcarski ma sens; jeśli dalej
daje 0/N, to potwierdzenie W12 i idziemy bez niego.

To jest tanie: 100 pojedynków to sekundy. Ale **nie budujemy na tym selekcji,
zanim nie zobaczymy wariancji.**

---

## Źródła

- [Engineering the cbh1 Promoter of *Trichoderma reesei* … Replacing the Binding Sites of a Transcription Repressor ACE1 to Those of the Activators — J. Agric. Food Chem.](https://pubs.acs.org/doi/abs/10.1021/acs.jafc.9b05452)
- [Influence of cis Element Arrangement on Promoter Strength in *Trichoderma reesei* — Appl. Environ. Microbiol.](https://journals.asm.org/doi/full/10.1128/aem.01742-17) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5734013/)
- [Construction of a cellulase hyper-expression system in *Trichoderma reesei* by promoter and enzyme engineering — Microb. Cell Fact.](https://microbialcellfactories.biomedcentral.com/articles/10.1186/1475-2859-11-21)
- [Transcriptional Regulation of xyn1, Encoding Xylanase I, in *Hypocrea jecorina* — Eukaryot. Cell](https://journals.asm.org/doi/abs/10.1128/ec.5.3.447-456.2006)
- [Xyr1 Regulates both the Hydrolytic Enzyme System and d-Xylose Metabolism — Eukaryot. Cell](https://journals.asm.org/doi/10.1128/ec.00211-06)
- [Identification of specific binding sites for XYR1 — PubMed](https://pubmed.ncbi.nlm.nih.gov/19393758/)
- [Controlling AOX1 promoter strength in *Pichia pastoris* by manipulating poly(dA:dT) tracts — Sci. Rep.](https://www.nature.com/articles/s41598-018-19831-y)
- [Promoter engineering with programmable upstream activating sequences in *Aspergillus niger* — Microb. Cell Fact.](https://link.springer.com/article/10.1186/s12934-025-02642-y)
