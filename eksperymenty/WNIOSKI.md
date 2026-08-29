# WNIOSKI — rejestr globalny

Jeden plik do przeczytania przed zgłoszeniem. Uzupełniany po każdym eksperymencie.

Konwencja statusów: **[OTWARTE]** nie zmierzone · **[POTWIERDZONE]** / **[OBALONE]**
z danymi · **[REWIZJA]** wcześniejszy wniosek okazał się błędny metodologicznie.

---

## Stan przeniesiony z fazy 1 (`hipotezy.ipynb`)

| # | wniosek | status | konsekwencja dla zgłoszenia |
|---|---|---|---|
| W1 | Gradient głowicy promotorowej siedzi w 2,2 % długości (783–800), reszta ~0,03 | **[POTWIERDZONE]** ale przyczyna **[OTWARTE]** → E02 | jeśli biologia: rdzeń to jedyne miejsce warte edycji; jeśli artefakt: 30 % planu do wyrzucenia |
| W2 | `ile_kodow` nie steruje agresywnością (×16 → +12 % dystansu) | **[POTWIERDZONE]** | nie kręcić tym pokrętłem licząc na różnorodność |
| W3 | Dekoder rozrzuca zmiany poza rdzeniem (2,17 % trafień w 2,25 % sekwencji = losowo) | **[POTWIERDZONE]** | rdzeń trzeba edytować **ręcznie po dekodowaniu**, nie przez `/edycje` |
| W4 | Sędzia mierzy prototypowość, nie siłę; wysycony powyżej progu | **[POTWIERDZONE]** | wyłącznie bramka „czy to nadal promotor" |
| W5 | Losowe podstawienia nigdy nie biją dzikiego (0/80, do 640 zmian) | **[POTWIERDZONE]** | przestrzeń liter jest martwa jako przestrzeń przeszukiwań |
| W6 | Wspinaczka pod Sędziego plateau po 1 kroku (1/20 przyjęć) | **[POTWIERDZONE]** | wspinaczka nie padła jako algorytm — padło **kryterium**. Wraca do gry, jeśli E01 da skalar |
| W7 | Kanał gatunku ma punkt stały: 9 → 1 → 0 rekomendacji, 10 zmian od dzikiego | **[POTWIERDZONE]** | jedyna potwierdzona hipoteza fazy 1; wariant przegrywa u Sędziego, co jest **oczekiwane** i nie jest powodem do odrzucenia |
| W8 | Nasze zgłoszenie: 100 sekwencji, mediana 100 zmian, 2,3 zmiany w rdzeniu, jedna rodzina | **[POTWIERDZONE]** | mechaniczne wyjaśnienie ALL100 #1 / TOP10 #2 |

---

## Nowe wnioski fazy 2

### W9 — Nagłówek `/mapa` może zawierać funkcję celu

**[OTWARTE]** → E01

Legenda API zastrzega nieporównywalność **wyłącznie dla `wagaP`**. Pola
`zmian_pod_gatunek`, `blad_odtworzenia`, `nie_rekonstruuje` i `rekon_frakcja`
to bezwzględne liczby, nie normalizowane w obrębie sekwencji. Jeśli wariują
między sekwencjami, mamy skalar do minimalizowania — czyli dokładnie to, czego
brakowało w tabeli „czego nie masz" z komórki 29 fazy 1.

Szczególnie `zmian_pod_gatunek`: to licznik niedopasowania do szczepu P1,
malejący 9 → 1 → 0 w W7. Wyrocznia ocenia **w kontekście P1**, Sędzia gatunku
nie widzi. Zgodność kierunku jest tu argumentem, nie przypadkiem.

> Konsekwencja, jeśli potwierdzone: wraca wspinaczka (W6 padła tylko przez
> kryterium), wraca selekcja puli, wraca porównywanie hipotez bez zużywania
> okna 5 minut. To najwyżej rokujący pojedynczy wynik całej fazy 2.

### W10 — Szczyt `wagaP` może być artefaktem brzegowym

**[OTWARTE]** → E02

Faza 1 zinterpretowała okno 783–800 jako rdzeń promotora przy TSS i na tej
podstawie przydzieliła mu 30 sekwencji w planie. Alternatywa — wrażliwość
sieci konwolucyjnej na krawędź wejścia — nie została odrzucona.

Rozstrzyga **rotacja**: przesunięcie treści o *k* pozycji przy zachowaniu
całej lokalnej zawartości. Jeśli szczyt idzie za treścią → biologia.
Jeśli zostaje na końcu → artefakt. Permutacja i sekwencja losowa są
kontrolami wspierającymi.

### W11 — Skorelowane warianty nie kupują TOP10

**[POTWIERDZONE]** analitycznie, do sprawdzenia empirycznie w E05

Symulacja z komórki 34 fazy 1 zakłada, że ryzykowne sekwencje są **niezależnymi**
losowaniami. Plan 30/30/20/10/10 ma pięć hipotez, nie sto losowań — jeśli
hipoteza jest zła, cały blok pada razem. TOP10 to statystyka pozycyjna:
nagradza efektywną liczbę niezależnych prób.

> Konsekwencja: 10–12 bloków po 8 zamiast 5 po 20–30. Wewnątrz bloku **skan
> parametru** (TATA na 722, 726, 730 … 766), nie losowy jitter wokół jednego punktu.

### W12 — Hipotezy działają na rozłącznych zbiorach pozycji

**[POTWIERDZONE]** z danych fazy 1, efekt **[OTWARTE]** → E04

| hipoteza | pozycje | źródło |
|---|---|---|
| gatunek (W7) | 154, 287, 362, 430, 434, 648, 750, 754, 778 + 276 w iteracji 2 | `zmien_na` |
| CreA | 560–565 | skan IUPAC `SYGGRG` |
| rdzeń | 783–800 | `wagaP` > 0,5 |

Zbiory są **rozłączne**, więc edycje się nie znoszą i dają się złożyć.
W planie zgłoszenia fazy 1 każda hipoteza występuje osobno i **nie ma ani
jednej kombinacji** — mimo że kombinacja jest najtańszą drogą do sekwencji
lepszej niż każdy pojedynczy składnik.

### W13 — Sekwencje „silnych promotorów" z modelu językowego są zmyślone

**[POTWIERDZONE]**, pomiar poniżej

Zbiór przekazany jako Ptef1 / PcDNA1 / Ppdc1 / PgpdA / Pcbh1 / Pnag1 / Pxyn2:

```
długość              840 pz          (wymagane 800 — nie przeszłyby filtra)
okres powtórzenia    48 pz, zgodność 1,000
unikalnych 12-merów  26 z 829
różnych 4-merów      10 z 256        → entropia 2,89 bit zamiast ~8
skład                A245 G210 C193 T192
```

To `AGCTAGCTAGCTAGG` powtórzone w kółko, z innym prefiksem dla każdej „nazwy".
Dodatkowo `AGCT` jest palindromem, więc konstrukt składałby się w spinki.

> Konsekwencja: **nie wchodzą ani do puli, ani do zbioru referencyjnego**.
> Materiał referencyjny to `data/promotory_100.csv` (100 naturalnych promotorów,
> 19 gatunków *Trichoderma*, z materiałów hackathonu) — patrz E03.
> Jako slajd: przykład zatrutych danych wejściowych i tego, jak je wykryć
> bez dostępu do prawdy — sama statystyka sekwencji wystarczy.

### W14 — Naturalne promotory jako drugi punkt startowy

**[OTWARTE]** → E03

Otwarte pytanie 4 z briefu, nigdy niesprawdzone, bo pliku nie było w `data/`.
Trzy rzeczy do wyciągnięcia: czy któryś bije dzikiego u Sędziego (drugi punkt
startowy), jaki jest konsensus ostatnich 18 pz w promotorach wyrównanych do TSS
(materiał do edycji rdzenia w E04), i czy klastrują się na archetypy
(bloki hipotez do portfela).

---

## Rejestr decyzji — co robimy w zależności od wyników

Uzupełniać po każdym eksperymencie. Puste pola = jeszcze nie wiemy.

| pytanie | odpowiedź | data | wpływ na zgłoszenie |
|---|---|---|---|
| E01: czy `blad_odtworzenia` wariuje? | | | |
| E01: czy `zmian_pod_gatunek` wariuje? | | | |
| E01: czy skalar koreluje z werdyktem Sędziego? | | | |
| E02: czy szczyt `wagaP` idzie za treścią? | | | |
| E03: czy naturalny promotor bije dzikiego? | | | |
| E03: jaki konsensus w oknie 783–800? | | | |
| E04: efekt główny czynnika A (gatunek)? | | | |
| E04: efekt główny czynnika B (CreA)? | | | |
| E04: efekt główny czynnika C (rdzeń)? | | | |
| E04: najsilniejsza interakcja? | | | |
| E05: pozycja TOP10 po zgłoszeniu? | | | |

---

## Historia zgłoszeń

| # | plik | skład | ALL100 | TOP10 | punkty | wniosek |
|---|---|---|---|---|---|---|
| 1 | `pula.fasta` | `hybryda`: 1 z mapy + 49 `/edycje` + 50 krzyżówek | 1 | 2 | 17,5 | 5 startujących; 3 niezależne korzenie (W22) |
| 2 | `v3.fasta` | przesiew E07, 100/100 bramka, 56 korzeni | 5 | 4 | 13,0 | 10 startujących — skala rangowa inna, nieporównywalne wprost |
| 3 | `v4.fasta` | E08, 100/100 bramka, **100 korzeni** | **4** | **4** | **14,0** | **TOP10 bez zmiany mimo 56→100 korzeni → K1 wyczerpany** |

---

## Faza 3 — wyniki E02 i E03 (uruchomione 2026-08-29)

### W10 — ROZSTRZYGNIĘTE: szczyt `wagaP` to **artefakt brzegowy**

**[OBALONE]** — interpretacja biologiczna okna 783–800 upada.

Bateria 15 sekwencji (E02) + 100 naturalnych promotorów (E03), łącznie
**101 różnych sekwencji**. Wynik `argmax(wagaP)`:

```
poz. 788 : 100 ze 101 sekwencji
poz.  13 :   1 ze 101
```

Szczyt nie drgnął dla: rotacji o 100/200/400/600 pz (treść przesunięta,
szczyt został), odwrócenia, trzech permutacji, trzech sekwencji losowych,
podmiany całego rdzenia na losowy i na poli-A. **Sygnał nie zależy od treści** —
zależy wyłącznie od odległości od krawędzi wejścia.

> **Konsekwencja:** wszystkie plany oparte na „rdzeniu promotora przy TSS"
> tracą uzasadnienie. W planie portfela było na to ~30 sekwencji.
> `wagaP` **nie jest** mapą ważności biologicznej.

Zastrzeżenie: **masa** gradientu w tym oknie nadal zależy od treści
(0,10–0,38 dla naturalnych, dziki 0,32). Artefaktem jest *lokalizacja* szczytu,
niekoniecznie cała informacja w `wagaP`.

### W12 — Żaden naturalny promotor nie bije dzikiego

**[POTWIERDZONE]** — 0/100 naturalnych promotorów *Trichoderma* (19 gatunków)
wygrało z dzikim u Sędziego. Chimery dziki×naturalny: 0/15.

Razem z W5 (0/80 losowych) i W6 (plateau) domyka obraz: **Sędzia praktycznie
nigdy nie stawia niczego nad dzikim.** Jako funkcja celu jest bezużyteczny;
jako bramka „czy to promotor" — działa.

### W13 — `blad_odtworzenia` to detektor pochodzenia sekwencji

**[POTWIERDZONE]** — rozkłady **rozłączne**, bez ani jednego przypadku brzegowego:

| zbiór | n | `blad_odtworzenia` (min–mediana–max) |
|---|---|---|
| sekwencje z dekodera (nasza pula) | 44 | **16 – 21,5 – 27** |
| naturalne promotory *Trichoderma* | 100 | **63 – 77 – 95** |
| dziki `pks1` | 1 | 80 |
| `z_mapy` (dziki + 9 ręcznych zmian) | 1 | 79 |

Luka 28–62 jest **pusta**. Jedno wywołanie `/mapa` wystarcza, by rozstrzygnąć,
czy sekwencja pochodzi z dekodera, czy jest prawdziwym DNA.

> **Konsekwencja dla zgłoszenia:** cała nasza wgrana pula ma wartość ~21 przy
> naturalnych ~77. Jeśli Wyrocznia była trenowana na prawdziwych promotorach,
> sto sekwencji leżących dokładnie na rozmaitości autoenkodera jest
> systematycznie poza rozkładem treningowym. To **mierzalna, jednowymiarowa
> cecha odróżniająca nasze zgłoszenie od prawdziwych promotorów** — i darmowy
> regulator: chcąc „naturalności", celujemy w `blad_odtworzenia` ≈ 63–95.

### W14 — Nagłówek `/mapa` daje skalary, ale żaden nie przewiduje Sędziego

**[CZĘŚCIOWO OBALONE]** — rewizja W9.

Pola nagłówka **wariują** między sekwencjami (n=100 naturalnych):
`blad_odtworzenia` 63–95, `nie_rekonstruuje` 71–106, `zmian_pod_gatunek` 1–17,
`masa_rdzenia` 0,10–0,38. Czyli skalary istnieją.

Ale **nie separują** zwycięzców od przegranych u Sędziego (45 sekwencji naszej
puli, d Cohena): `masa_rdzenia` −0,45 · `blad_odtworzenia` −0,16 ·
`nie_rekonstruuje` −0,13 · `zmian_pod_gatunek` +0,15. Wszystkie poniżej progu
efektu średniego.

Dodatkowo `zmian_pod_gatunek` **nie wyróżnia P1**: dziki (prawdziwy promotor P1)
ma 9, mediana obcych gatunków też 9, a promotor *T. reesei* ma **1** — czyli
„lepiej dopasowany do P1" niż sam P1. To pole nie jest miarą przynależności
do szczepu i **nie nadaje się na funkcję celu**.

---

## Faza 4 — E01, E04, E06, E07 (uruchomione 2026-08-29)

> **Uwaga o numeracji.** Sekcja „Faza 3" powyżej użyła powtórnie numerów
> W12–W14, które w „Fazie 2" znaczą co innego. Nowe wnioski numerujemy od **W15**
> i nie ruszamy starych, żeby odwołania w `PLAN.md` nie przestały pasować.

### W15 — SPROSTOWANIE: pola nagłówka `/mapa` były gubione przez cały pipeline

**[REWIZJA]** — usterka narzędziowa, nie wynik.

`wspolne/metryki.py` czytał pola z `odp["naglowek"]`, a API zwraca je na
**najwyższym poziomie** odpowiedzi. Efekt: `metryki_mapy` zapisywało `None`
we wszystkich czterech polach kandydujących na funkcję celu — czyli dokładnie
w tych, o które chodziło w E01.

Zasięg: `E03/wyniki.json` miał `blad_odtworzenia = None` dla wszystkich stu
promotorów. Liczby cytowane w W13/W14 „Fazy 3" pochodziły z **doraźnego skryptu**
(`data/naglowki_naturalne.json`), a nie z eksperymentu. Same liczby okazały się
poprawne (dziki = 80 potwierdzone niezależnie w E01), ale **nie były
odtwarzalne z repozytorium** — a to jest ta sama klasa błędu, przed którą
ostrzega reguła 1 z README.

Poprawione (`nag = odp.get("naglowek") or odp`), E01 i E03 przeliczone.

### W16 — Sędzia jest w pełni powtarzalny

**[POTWIERDZONE]** — 7 par × 8 powtórzeń tego samego pojedynku: **8/8 albo 0/8**,
bez ani jednego przypadku pośredniego. `dziki vs dziki` → 0/8, czyli remis
rozstrzygany jest na korzyść bazy i nie ma losowej przewagi.

> To jest warunek wstępny wszystkiego poniżej. Bez niego zdania typu
> „72 % kontra 6 %" byłyby nieodróżnialne od rzutów monetą.

### W17 — E01: skalary istnieją i są deterministyczne, ale **nie są miarą jakości**

**[CZĘŚCIOWO POTWIERDZONE]** — bateria 120 sekwencji, 116 z werdyktem.

| hipoteza | wynik |
|---|---|
| E01.1 `blad_odtworzenia` wariuje | **POTWIERDZONA** — 15–99, sd 18,5 |
| E01.2 `zmian_pod_gatunek` wariuje | **POTWIERDZONA** — 0–11, sd 2,1 |
| E01.3 oba deterministyczne | **POTWIERDZONA** — dziki ×5 → identyczne co do jednostki |
| E01.4 koreluje z Sędzią | **OBALONA** — patrz W18 |
| E01.5 `zmian_pod_gatunek` niezależny od Sędziego | **POTWIERDZONA** (d = +0,26) |

Rozstrzyga jednak **kontrola monotoniczności**, bo to ona mówi, czy metryka
jest w ogóle miarą czegokolwiek:

| sekwencja | zmian od dzikiego | `blad_odtworzenia` |
|---|---|---|
| dziki | 0 | 80 |
| losowe podstawienia | 5 | 81 |
| losowe podstawienia | 50 | 85 |
| losowe podstawienia | 200 | **84** |
| przetasowany | 612 | 99 |
| **jedno przejście przez dekoder** | ~100 | **~21** |

**Dwieście losowych podstawień rusza metrykę o 4. Jedno przejście przez dekoder
o −59.** Znane uporządkowanie *a priori* (5 < 50 < 200) **nie jest odtworzone**.

> `blad_odtworzenia` nie jest miarą jakości ani odległości od dzikiego —
> jest **detektorem pochodzenia**: mówi, czy sekwencja leży na rozmaitości
> autoenkodera. Wg kryterium z `E01/PLAN.md` („wariuje, ale nie jest
> monotoniczne na kontroli") wolno go używać **wyłącznie do odsiewania
> skrajności, nie do rankingu**. Wspinaczka z W6 **nie wraca**.

### W18 — Żaden skalar nagłówka nie przewiduje werdyktu Sędziego

**[POTWIERDZONE]** — i jest to lekcja o konfundacji.

Na całej baterii `blad_odtworzenia` wygląda na predyktor (d Cohena = −0,48).
Wewnątrz **jednorodnej pod względem pochodzenia** puli 92 sekwencji efekt znika:

| metryka | d Cohena (cała bateria) | d Cohena (wewnątrz puli) |
|---|---|---|
| `blad_odtworzenia` | −0,48 | **+0,06** |
| `nie_rekonstruuje` | −0,45 | +0,15 |
| `masa_rdzenia` | −0,39 | −0,41 |
| `srodek_masy` | −0,06 | −0,45 |
| `zmian_pod_gatunek` | −0,00 | +0,26 |

Efekt międzygrupowy był w całości **artefaktem składu próby**: wszyscy zwycięzcy
pochodzili z dekodera, a wszystkie sekwencje spoza dekodera przegrywały.
Zostają `masa_rdzenia` i `srodek_masy` z |d| ≈ 0,4 — przedział ufności dotyka
zera (AUC 0,33 wewnątrz `hyb_*`, 0,43 wewnątrz `nav_*`), więc **na scorer to za mało**.

### W19 — E04: z czterech czynników działa jeden, i to nie ten biologiczny

**[POTWIERDZONE]** — pełne 2⁴ × 3 repliki = 48 sekwencji. **0/48 bije dzikiego,
0/48 bije własnego rodzica.**

Czynnik C nie został wycięty mimo werdyktu ARTEFAKT z E02 (`--wymus-c`):
E02 obaliło *lokalizację* szczytu, a nie całą informację w oknie, i to właśnie
`masa_rdzenia` była w W18 najsilniejszym korelatem. Plan 2³ jest w środku jako
połowa C=0, więc nic nie stracono.

Efekty główne na `blad_odtworzenia` (rozstęp replik = **1,5**, to jest próg szumu):

| czynnik | efekt | odczyt |
|---|---|---|
| **D** tło z dekodera | **−60,8** | 40× ponad szum — dominuje wszystko |
| **C** rdzeń | −3,0 | 2× szum, ale patrz interakcja |
| **A** gatunek | −0,7 | szum |
| **B** CreA | −0,2 | szum |

Czynnik **A działa, ale na własnej osi**: `zmian_pod_gatunek` −4,9 przy rozstępie
replik 0. Czynnik **B jest niewidoczny we wszystkich metrykach** — zgodnie
z przewidywaniem z `PLAN.md`, ale to znaczy też, że **nie mamy na niego żadnego dowodu**.

Najsilniejsza interakcja: **C×D na `masa_rdzenia` = +0,065** (3,4× rozstęp replik).
Konsensusowy rdzeń **obniża** masę rdzenia na tle dzikim i **podnosi** na tle
dekodera. Efekt główny C uśrednia zmianę znaku, więc jako liczba nic nie znaczy —
to jest przykład na to, po co w ogóle liczy się interakcje.

Druga interakcja warta uwagi: **A×D na `zmian_pod_gatunek` = +8,2**. Kanał gatunku
sprowadza dzikiego z 9 do 0, ale na tle dekodera nie ma już czego poprawiać
(wyjścia dekodera startują z 2–5). **Dopasowanie gatunkowe i dekoder robią
częściowo to samo.**

> Zrealizował się wiersz z tabeli decyzyjnej `E04/PLAN.md`:
> **„efekt D >> A,B,C → wygrywamy prototypowością, nie biologią".**

Zastrzeżenie projektowe do wypowiedzenia: przy D=0 wszystkie repliki są
**identyczne**, bo edycje A/B/C są deterministyczne. Rozstęp replik dla połowy
planu jest więc zerowy z konstrukcji, a nie z powtarzalności pomiaru.

### W20 — E06: liczy się **ziarno**, nie operator

**[POTWIERDZONE]** — najważniejszy wynik tej fazy.

Punkt wyjścia: wgrana pula rozbita na sposób powstania daje dwunastokrotną różnicę
(`hyb_*` 36/50 = 72 %, `nav_*` 3/49 = 6 %). Ale rodzicami krzyżówek byli
**zwycięzcy turnieju**, więc efekt operatora był pomieszany z preselekcją.

| ramię | bije dzikiego | bije własnego rodzica |
|---|---|---|
| R1 surowe `/edycje` | 0/16 | — |
| **R2 krzyżówka dwóch PRZEGRANYCH** | **0/16** | 0/16 |
| R3 krzyżówka dwóch zwycięzców | 9/16 (56 %) | 0/16 |
| R4 zwycięzca × dziki | 8/16 (50 %) | 0/16 |
| **R5 mutacja zwycięzcy o ten sam dystans** | **8/16 (50 %)** | 0/16 |
| R6 drugie pokolenie | 11/16 (69 %) | 0/16 |

Trzy wnioski, każdy z własnej kontroli:

1. **E06.1 OBALONA — operator sam z siebie nie działa.** Krzyżowanie przegranych
   siedzi dokładnie tam, gdzie surowy dekoder: na zerze.
2. **E06.2 OBALONA — to nie jest rekombinacja.** Zwykła mutacja o ten sam dystans
   (50 %) daje to samo co krzyżowanie (56 %). Liczy się **od kogo zaczynasz**,
   a nie **co robisz**.
3. **E06.3 OBALONA — nic nie bije własnego rodzica.** 0/80 tutaj, 1/390 w E07,
   czyli **1 przypadek na 494**.

> Konsekwencja: cała optymalizacja jest loterią rozstrzyganą na etapie
> **losowania ziarna**. Wszystko, co robimy potem, kopiuje ziarno z połowicznym
> powodzeniem i nigdy go nie przewyższa. Jedyna droga w górę to **znaleźć lepsze
> ziarno**; jedyna droga do TOP10 to **znaleźć wiele niezależnych ziaren**.

### W21 — E07: ziarna są rzadkie (~8 %), a parametry dekodera nie sterują trafieniami

**[POTWIERDZONE]** — 784 losowania, 65 ziaren.

Zbalansowany test (poziom 2, **równe n = 96** na komórkę):

| `ile_kodow` | trafień | odsetek |
|---|---|---|
| 4 | 0/96 | **0 %** |
| 8 | 7/96 | 7,3 % |
| 12 | 5/96 | 5,2 % |
| 16 | 6/96 | 6,2 % |
| 24 | 11/96 | 11,5 % |
| 32 | 8/96 | 8,3 % |

Poza martwym `ile_kodow = 4` wszystko leży płasko w granicach 5–11 %,
a 95-procentowe przedziały zachodzą na siebie. `poziom = 0` nie dał ani jednego
trafienia (0/48, p ≈ 0,02); poziomy 1 i 2 działają.

> Ta tabela istnieje wyłącznie dlatego, że pierwszy, **niezbalansowany** przesiew
> pokazywał ładny monotoniczny trend 7,1 % → 9,2 % → 11,2 %. Był artefaktem
> doboru próby: szeroki przesiew próbkował tylko te komórki, które trafiły
> w rzadkiej siatce. **Bez kontroli z równym n obalilibyśmy W2 na podstawie
> trzech trafień.**

Pozostałe pomiary: 65 ziaren tworzy **65 osobnych skupień** przy progu 40 pz —
żadna para nie jest tą samą rodziną. Wydajność chmury wokół ziarna: 58 %
(E06/R5 dało 50 %, zgodnie).

### W22 — Wgrane zgłoszenie to **trzy** losowania, nie trzydzieści dziewięć

**[POTWIERDZONE]** — mechanizm W8, teraz z liczbą.

`pula.fasta` ma 39/100 sekwencji przechodzących bramkę, ale 36 z nich to rodzina
`hyb_*` — dzieci **trzech** zwycięzców z jednego zaciągu. TOP10 jest statystyką
pozycyjną, więc widzi **trzy niezależne losowania**. To jest dokładnie ta
korelacja, przed którą ostrzegał W11, tylko wcześniej nie było wiadomo,
że rodzina ma korzeń w trzech sekwencjach.

### W23 — Usterka: blok „zabezpieczenia ALL100" składał się z najsłabszej części puli

**[POTWIERDZONE]**, naprawione.

`blok_01` brał **pierwsze 12 sekwencji z pliku**, a `pula.fasta` zaczyna się od
rodziny `nav_*` (6 % przejść). Blok, który w `PLAN.md` jest opisany jako
„zabezpieczenie ALL100 — wiemy, że daje pozycję 1", przechodził bramkę **0/12**.
Po zmianie selekcji na „przechodzące bramkę": **12/12**.

---

## Porównanie portfeli (bramka Sędziego, pomiar lokalny przed zgłoszeniem)

| portfel | skład | przechodzi bramkę | niezależnych losowań |
|---|---|---|---|
| **v1** `pula.fasta` | wgrane zgłoszenie, `hybryda` | 39/100 (39 %) | **3** |
| **v2** `v2.fasta` | plan 12 bloków (E05) | 13/100 (13 %) | ~12 hipotez |
| **v3** `v3.fasta` | przesiew E07 | **100/100 (100 %)** | **100** |

W v2 wszystkie przejścia pochodzą z bloku 1 (12/12) i jednego dopełnienia.
Bloki 2–12 dają **0/78**.

> **Zastrzeżenie, bez którego ta tabela wprowadza w błąd.** Bramka Sędziego mierzy
> **prototypowość**, nie siłę promotora (W4). Bloki 2–12 przegrywają, bo zmieniają
> wymiary, których Sędzia z definicji nie widzi: gatunek, derepresję kataboliczną,
> kontekst genu. Zero na bramce **nie znaczy „słabe"** — znaczy „nie mamy na to
> żadnego lokalnego dowodu". Symetrycznie: v3 maksymalizuje jedyne dostępne proxy
> i jest przez to **najbardziej narażony na prawo Goodharta** z sekcji 6 briefu.
> Jedyną przesłanką, że bramka w ogóle koreluje z Wyrocznią, jest to, że pula
> o 39 % przejść dostała ALL100 #1.

---

## Rejestr decyzji — wypełniony

| pytanie | odpowiedź | wpływ na zgłoszenie |
|---|---|---|
| E01: czy `blad_odtworzenia` wariuje? | **tak**, 15–99, deterministycznie | ale niemonotonicznie → tylko odsiewanie skrajności |
| E01: czy `zmian_pod_gatunek` wariuje? | **tak**, 0–11 | osobna oś, nieskorelowana z Sędzią |
| E01: czy skalar koreluje z werdyktem Sędziego? | **nie** (d = +0,06 wewnątrz puli) | **brak scorera** — selekcja tylko przez bramkę |
| E02: czy szczyt `wagaP` idzie za treścią? | **nie** (artefakt brzegowy) | ale `masa_rdzenia` zależy od treści → C zmierzone, nie wycięte |
| E03: czy naturalny promotor bije dzikiego? | **nie**, 0/100 | nie ma drugiego punktu startowego |
| E03: jaki konsensus w oknie 783–800? | `CAAGAAACCTAATCCAAC` | użyty jako czynnik C w E04 |
| E04: efekt główny A (gatunek)? | na własnej osi −4,9; na jakości ~0 | zostaje jako hipoteza bez dowodu |
| E04: efekt główny B (CreA)? | **0 w każdej metryce** | niewidoczne dla Nawigatora — brak dowodu |
| E04: efekt główny C (rdzeń)? | pozorny; realna jest interakcja C×D | efekt główny bez sensu przy zmianie znaku |
| E04: najsilniejsza interakcja? | **C×D** na `masa_rdzenia` (+0,065) | rdzeń działa inaczej na każdym tle |
| E06: operator czy dziedziczenie? | **dziedziczenie** — krzyżowanie przegranych 0/16 | portfel budować z ziaren, nie z operatorów |
| E07: ile niezależnych ziaren? | **65** z 784 losowań (8,3 %) | v3: 100 niezależnych ziaren |
| E05: pozycja TOP10 po zgłoszeniu? | *nie wgrano — decyzja użytkownika* | |

---

## Co z tego idzie na prezentację

Cztery rzeczy, z których **trzy są negatywne** — i to jest zaleta, bo każda ma
kontrolę, która ją unieważniła:

1. **E06 — kontrola, która obaliła nasz najlepszy wynik.** Mieliśmy 72 % vs 6 %
   i gotową opowieść o sile rekombinacji. Jedno ramię (krzyżowanie przegranych,
   0/16) pokazało, że operator nie robi nic, a całą robotę wykonuje preselekcja
   rodzica. Drugie ramię (mutacja o ten sam dystans, 50 %) domknęło dowód.
2. **E07 — kontrola, która obaliła nasz własny trend.** Niezbalansowany przesiew
   dawał ładną monotoniczność po `ile_kodow`; przy równym n okazała się
   artefaktem doboru próby.
3. **W18 — konfundacja pochodzeniem.** Ten sam skalar ma d = −0,48 między grupami
   i +0,06 wewnątrz grupy. Podręcznikowy przykład na to, dlaczego korelacja
   liczona na zlepku prób nie znaczy nic.
4. **W15 — usterka narzędziowa, która przez trzy eksperymenty produkowała `None`.**
   Liczby w raporcie były prawdziwe, ale pochodziły z doraźnego skryptu obok
   pipeline'u. Odtwarzalność jest częścią wyniku, nie dodatkiem do niego.



### W24 — K1 wyczerpany: liczba niezależnych ziaren nie rusza już TOP10

**[OBALONE]** — oczekiwanie z W22, zmierzone w E08.

v3 (56 niezależnych korzeni) i v4 (**100** korzeni, 0/4950 par poniżej progu
skupienia) dają **tę samą pozycję TOP10 — 4**. Zmieniło się tylko ALL100
(5 → 4), co daje +1 punkt.

TOP10 zależy od **górnego ogona rozkładu**, z którego losujemy, a nie od liczby
losowań: 56 i 100 prób z tego samego rozkładu mają niemal identyczne maksimum.
**Rozkład ziaren dekodera ma sufit i jesteśmy przy nim.**

> Konsekwencja: dalsze losowanie z `/edycje` jest stratą czasu. Potrzebny jest
> **inny rozkład** — hipotezy gatunkowe (K1b), naturalność (K5) albo test
> rozjazdu proxy (K4). Czubek tabeli (18,0 pkt, trzy drużyny) jest o 4 punkty
> wyżej, czyli o dwie pozycje w każdej kategorii.

Zastrzeżenie: przy dziesięciu startujących skala rangowa ma krok 1 punktu,
więc różnice mniejsze niż jedna pozycja są niewidoczne. Nie wyklucza to
poprawy surowego wyniku, której ranking nie pokazuje.

---

## Faza 5 — E10: pierwsze wnioski BIOLOGICZNE (offline, 0 wywołań API)

Do tej pory wszystkie 24 wnioski dotyczyły **architektury narzędzi**, nie
promotorów. E10 jest analizą porównawczą dzikiego `pks1` wobec stu naturalnych
promotorów *Trichoderma* — liczoną z `E03/wyniki.json`, bez sieci.

### W25 — Rdzeń promotora istnieje i wychodzi z konserwacji, nie z modelu

**[POTWIERDZONE]** — informacja pozycyjna w 100 promotorach wyrównanych do TSS:

```
poz.   1-700    IC 0,019-0,030 bit     tło
poz. 701-750    IC 0,042               2,0 × tło
poz. 751-800    IC 0,055               2,6 × tło
poz. 798 (TSS-2)  IC 0,525  ->  A w 62/100    25 × tło    (dziki ma G)
```

Silna preferencja puryny dwie zasady przed końcem = element **Inr**.
To zastępuje martwą historię o oknie 783–800 z `wagaP` (W10: artefakt brzegowy)
sygnałem wyprowadzonym z danych biologicznych, niezależnym od modelu.

### W26 — Rdzeń `pks1` jest **normalny** → nie ma czego w nim naprawiać

**[POTWIERDZONE]** — log-odds wobec PWM ze stu naturalnych:

| okno | naturalne (mediana) | dziki | percentyl |
|---|---|---|---|
| rdzeń 751–800 | 2,97 | **3,67** | **52 %** |
| kontrola 401–450 | 1,35 | −0,33 | 25 % |

Kontrola pokazuje, że PWM w ogóle działa. **Wynik negatywny: blok „edycja
rdzenia" wypada z planu** — dziki ma rdzeń taki, jak reszta rodzaju.

### W27 — `pks1` nie ma ani jednego miejsca CCAAT, a 81 % rodzaju ma

**[POTWIERDZONE]** — skan obu nici (`CCAAT` + `ATTGG`):

| motyw | dziki | mediana naturalnych | % z ≥ 1 |
|---|---|---|---|
| **CCAAT / ATTGG** | **0** | **2** | **81 %** |
| CreA | 2 | 2 | 92 % |
| Inr-podobny | 1 | 1 | 65 % |
| TATAAA | 1 (na −457) | 0 | 43 % |
| GC-box | 0 | 0 | 33 % |

CCAAT to **jedyny** motyw, w którym dziki odstaje; przy pozostałych jest na
medianie. Wiąże go kompleks **CBC/HAP** (HapB–HapC–HapE) — udokumentowany
ogólny aktywator u grzybów strzępkowych: zagina DNA, przesuwa nukleosom,
otwiera region dla maszynerii podstawowej.

Naturalne trzymają te miejsca w pasie −500…−200 (mediana −388, najgęściej
−300…−201). Dziki jest **jedno podstawienie** od pełnego CCAAT w 22 miejscach.

> **Zastrzeżenie, które mówimy pierwsi:** to **nie jest anomalia statystyczna**.
> Z samego składu zasad oczekujemy 1,62 trafienia, `P(0) = 0,20`; zera ma też
> 19/100 naturalnych. Nie twierdzimy „`pks1` jest zubożony" — twierdzimy
> „81 % rodzaju niesie element aktywujący, którego `pks1` nie ma, a instalacja
> kosztuje jedno podstawienie". Do decyzji inżynierskiej to wystarcza.

### W28 — Konsekwencje dla planu: trzy bloki wypadają, jeden powstaje

| blok | los | powód |
|---|---|---|
| edycja rdzenia 783–800 | **wypada** | W10 (artefakt) + W26 (rdzeń w normie) |
| TATAAA w −80…−30 | **wypada** | tylko 43 % rodzaju ma TATAAA, a mediana to 0 — *Trichoderma* jest w większości TATA-less; dziki ma TATA na −457 |
| rozbicie CreA | **wypada** | dziki ma 2 miejsca, mediana rodzaju też 2 — brak przesłanki porównawczej (+ W19: efekt 0) |
| **naszczepienie CCAAT** | **powstaje** | W27 |

`v8_ccaat.fasta` = 100 ziaren z v4 (100 niezależnych skupień) + naszczepione
miejsca CCAAT. Zachowuje różnorodność z K1 i dokłada wymiar, na który
narzędzia są ślepe. 100/100 ziaren dostało miejsce, 0 odrzuconych w walidacji.

> Uwaga na W5: obalone były **losowe** podstawienia. Tutaj każda zmiana tworzy
> **nazwane miejsce wiązania białka** w pozycji wziętej z rozkładu naturalnego.
> Sędzia tego nie zobaczy (mierzy prototypowość dekodera) — i to nie jest powód
> do odrzucenia.


### W25 — LINIA BAZOWA: dziki jest DUŻO gorszy niż nasze portfele

**[POTWIERDZONE]** — E10/B0, pomiar, który unieważnia W24 i „centralny fakt"
z `PLAN_BIOLOGICZNY.md`.

`v9_B0_linia_bazowa.fasta` = 100 kopii dzikiego, każda z **dokładnie jednym**
podstawieniem (GC 47,4–47,6 %, `blad_odtworzenia` 80–82 przy dzikim 80).

| zgłoszenie | zmiana wobec dzikiego | TOP10 | ALL100 | punkty |
|---|---|---|---|---|
| **B0 linia bazowa** | **1 pz** | **9** | **8** | **5,0** |
| v8 CCAAT | 5–15 pz | 5 | 4 | 13,0 |
| v4 / v5 dekoder | ~100 pz | **4** | 4 | **14,0** |

**Nasza optymalizacja działa i to mocno: pięć pozycji rankingu nad punktem
wyjścia.** Instrument jest w pełni zdolny odróżnić dobre od złego — hipoteza W2
(„poprawa poniżej rozdzielczości skali") upada dla efektów tej wielkości.

> **Sprostowanie „centralnego faktu".** Wniosek „siedem mechanizmów, jeden
> wynik → nic nie działa" był **odwrotny do prawdy**. Wszystkie mechanizmy
> działają i **zbiegają do wspólnego plateau daleko powyżej dzikiego**.
> Brakowało jedynie punktu odniesienia, żeby to zobaczyć. Klasyczny przykład
> na to, że bez kontroli nie da się odróżnić „nic nie działa" od
> „wszystko działa tak samo dobrze".

### W26 — CCAAT odzyskuje ~90 % zysku przy 15 pz zamiast 100

**[POTWIERDZONE]** — reinterpretacja v8 w świetle W25.

Odległość od bazy w punktach: B0 = 5,0 → v8 = 13,0 → v4 = 14,0.
**Wstawienie kilku boksów CCAAT (5–15 pz) daje 8 z 9 punktów, które daje
cała maszyneria dekodera (~100 pz zmian i 594 losowania.)**

Wcześniej odczytaliśmy v8 jako „bez efektu", bo porównywaliśmy go z naszymi
portfelami zamiast z punktem wyjścia. To najbardziej wydajna edycja, jaką
znaleźliśmy — i jedyna z **mechanizmem molekularnym** (rekrutacja kompleksu
HAP/CBC), a nie z losowania.

### W27 — Bramka Sędziego jednak koreluje z Wyrocznią

**[REWIZJA W4]** — obawa o prawo Goodharta była przesadzona.

Sekwencje przechodzące bramkę (portfele dekodera) stoją 5 pozycji nad dzikim,
który bramki nie przechodzi. Sędzia nie jest bezużyteczny jako sygnał —
jest **zgrubny**, ale wskazuje właściwy kierunek. Nie unieważnia to W4
(mierzy prototypowość, nie siłę), ale unieważnia wniosek praktyczny
„bramka nic nie mówi o ocenie".

Zastrzeżenie: v8 (CCAAT) **nie przechodzi bramki**, a punktuje niemal tak samo
jak portfele, które ją przechodzą. Czyli bramka wskazuje **jedną z kilku**
dróg na plateau, nie jedyną.


### W28 — Ranking interwencji liczony od linii bazowej

**[POTWIERDZONE]** — dopiero W25 pozwolil ustawic te wyniki na jednej skali.

| interwencja | zmiana | TOP10 | ALL100 | punkty | **zysk nad baza** |
|---|---|---|---|---|---|
| B0 dziki + 1 pz | 1 pz | 9 | 8 | 5,0 | — |
| **B1 poli(dA:dT)** | ~64 pz | **6** | **8** | **8,0** | **+3,0** |
| v8 CCAAT | 5–15 pz | 5 | 4 | 13,0 | **+8,0** |
| v4 ziarno dekodera | ~100 pz | 4 | 4 | 14,0 | **+9,0** |

Dwie rzeczy warte odnotowania.

**Poli(dA:dT) dziala, ale slabo i asymetrycznie.** TOP10 poprawia sie o trzy
pozycje (9 -> 6), a **ALL100 nie rusza sie wcale** (8 -> 8). Czyli trakty
podnosza najlepsze sekwencje, ale nie podnosza sredniej — prawdopodobnie
przesuniecie skladu (mediana GC 47,5 % -> 41,8 %) kosztuje tyle, ile daje
otwarcie chromatyny. Hipoteza NFR nie jest obalona, ale **natezenie bylo za duze**.

**CCAAT pozostaje najwydajniejsza edycja.** 15 pz daje +8,0, czyli 89 % zysku
calej maszynerii dekodera przy ~7 % liczby zmienionych zasad.

> Konsekwencja dla kombinacji: os CCAAT i os ziarna sa mocne, os traktow slaba
> i szkodliwa dla sredniej. Portfel kombinowany powinien byc **CCAAT-centryczny**,
> z traktami najwyzej jako mniejszosciowy zaklad, a nie w 80 % sekwencji.


### W29 — SPROSTOWANIE W26 + pelne zestawienie od linii bazowej

**[REWIZJA]** — W26 opieral sie na blednym zalozeniu, ze `v8_ccaat.fasta` to
„dziki + CCAAT". Sprawdzenie zawartosci pliku: etykiety `z000_p1k16_6_ccaat`,
dystans od dzikiego **106–137 pz**. To sa **ziarna dekodera + boksy CCAAT**,
a nie 15-zasadowa edycja dzikiego. Zdanie „CCAAT odzyskuje 90 % zysku przy
15 pz" jest **nieprawdziwe** i zostaje wycofane.

Pelne zestawienie wszystkich zgloszen, uporzadkowane wg tego, co faktycznie
zawieraly:

| plik | baza | dodatek | punkty | TOP10 |
|---|---|---|---|---|
| `v11_B2_chimery_P1` | chimery z obcymi promotorami | — | **4,0** | 9 |
| `v9_B0_linia_bazowa` | dziki | 1 podstawienie | **5,0** | 9 |
| `v10_B1_poliAT` | dziki | trakty poli(dA:dT) | **8,0** | 6 |
| `v3` / `v4` / `v5` | ziarna dekodera | — / gatunek | **13–14** | 4 |
| **`v8_ccaat`** | **ziarna dekodera** | **boksy CCAAT** | 13,0 | 5 |

**`v8_ccaat` jest naszym najlepszym zgloszeniem.** Ranking pokazuje przy nas
znacznik **14:53:25**, a serwer trzyma najlepsze zgloszenie po **surowym**
wyniku TOP10 (pozycje sie przesuwaja wraz z polem, surowy wynik nie). Czyli
kombinacja **ziarno + CCAAT** ma nasz najwyzszy surowy TOP10 — wyzszy niz same
ziarna, mimo ze w momencie wgrania pokazywala gorsza *pozycje*.

### W30 — Baza ma znaczenie: obce DNA szkodzi

**[POTWIERDZONE]** — B2 (chimery z pieciu promotorow szczepu P1) dalo **4,0**,
czyli **ponizej linii bazowej (5,0)**. Jedyne zgloszenie gorsze od nietknietego
dzikiego.

Wszystko, co oddala sekwencje od promotora `pks1` w strone innego promotora,
**pogarsza wynik** — nawet jesli dawca pochodzi z tego samego szczepu.
Hipoteza „drugi punkt startowy" jest obalona ostatecznie (razem z W12: 0/100
naturalnych bilo dzikiego u Sedziego).

> Wniosek dla kierunku: **nie zmieniamy bazy.** Baza to `pks1` przepuszczony
> przez dekoder. Optymalizujemy wylacznie **dodatki** na tej bazie.


---

## Faza 6 — E15: konsensus, os pokolen i optimum wewnetrzne

### W31 — Sekwencja konsensusowa jest gorsza od kazdego ze skladnikow

**[POTWIERDZONE]** — pomiar, nie argument.

Uzgodnienie 100 sekwencji `v14_glebokosc` kolumna po kolumnie (uliniowienie
trywialne: 800 pz, ACGT, zero przerw — dekoder robi tylko podstawienia).

Konsensus **nie wraca do dzikiego**, wbrew przewidywaniu z W21: lezy 91 pz od
niego, a w **kazdej** z tych 91 kolumn dziki jest w mniejszosci, czesto
z udzialem 0,00. Dekoder ma silny powtarzalny podpis:

```
ziarno = konsensus (skladowa systematyczna, 91 pz) + ~51 pz wlasnego szumu
```

Ale jako kandydat konsensus przegrywa na obu osiach naraz:

| sekwencja | `blad_odtworzenia` | bramka |
|---|---|---|
| dziki | 80 | — |
| **konsensus** | **18** | **nie przechodzi** |
| najglebsze ziarno | **9** | przechodzi |

Rozstrzyga **drabina odszumiania** (ziarno przyciagane do konsensusu
w 0/25/50/75/100 % wlasnych pozycji, n = 6):

| frakcja | `blad` (mediana) | bramka |
|---|---|---|
| 0,00 | **14,0** | **6/6** |
| 0,25 | 21,0 | 2/6 |
| 0,50 | 21,0 | 2/6 |
| 0,75 | 23,5 | 0/6 |
| 1,00 | 18,0 | 0/6 |

> To, co wyglada na „szum" pojedynczego ziarna, **nie jest szumem** — jest
> czescia lezenia na rozmaitosci. Usrednienie dwoch poprawnych punktow
> zakrzywionej rozmaitosci daje punkt **poza** nia (srednia zdjec twarzy nie
> jest twarza; srednia punktow na sferze lezy w jej wnetrzu).
> Biologicznie to samo zdanie: **konsensus jest konstruktem statystycznym,
> nie sekwencja funkcjonalna.**

### W32 — Dekoder sam znalazl element Inr na pozycji 798

**[POTWIERDZONE]** — zbieznosc dwoch niezaleznych zrodel.

Dekoder zmienia `G -> A` na poz. 798 w **100/100** sekwencji. Niezaleznie
W25 zmierzyl w stu naturalnych promotorach: poz. 798 (TSS-2) ma **IC 0,525,
A w 62/100, 25 x tlo** — najbardziej informatywna kolumna calego okna.

Model uczony na sekwencjach i genomika porownawcza 19 gatunkow wskazuja
te sama zasade na tej samej pozycji, a dekoder nie widzial naszych stu
naturalnych promotorow. Najmocniejszy pojedynczy wynik biologiczny projektu.

### W33 — Blok B byl calym zyskiem v14; os pokolen ma optimum na 4

**[POTWIERDZONE]** — atrybucja v14 + trzy zgloszenia kontrolne.

Rozdzielenie blokow v14 (`E13/wyniki.json`):

| blok | co to bylo | `blad_odtworzenia` |
|---|---|---|
| A (45) | pokolenie 1, **wybrane 45 najglebszych ze 138** z 1600 losowan | 9 – 17 – 19 |
| B (45) | pokolenie 2/3, **bez selekcji na glebokosc** | **0 – 4 – 9** |

**44 z 45 sekwencji bloku B sa glebsze niz najglebsza z calego bloku A.**
Drugie przejscie przez dekoder daje za darmo wiecej glebokosci niz przesiew
1600 losowan pokolenia 1. Przesiewanie mocniej na pokoleniu 1 goni ogon,
ktory pokolenie 2 podaje z reki.

Pelna os (140 linii, pokolenia 2–8):

| pokolenie | `blad` min-med-max | dystans (med) | wynik zgloszenia |
|---|---|---|---|
| 1 (przesiew 1600) | 9 – 17 – 19 | 115 | w `v14` |
| 2 | 0 – 5 – 15 | 137 | |
| 3 | 0 – 3 – 11 | 154 | |
| **4** | 0 – 2 – 7 | **168** | **`v2` — POBILO v14** |
| 5 | 0 – 2 – 10 | 181 | |
| 6 | 0 – 2 – 7 | 192 | |
| 7 | 0 – 1 – 9 | 204 | |
| 8 | 0 – 1 – 11 | 216 | `v19` — **nie pobilo v2** |

**Os pokolen ma optimum WEWNETRZNE na pokoleniu ~4.** Nie jest monotoniczna:
`v14` (mieszanka pok. 1 + 2/3) przegrywa z `v2` (pok. 4), a `v19` (pok. 8)
tez przegrywa z `v2`. Glebokosc nasyca sie juz na 4 (mediana 2, min 0),
wiec za optimum odpowiada **dystans**, nie glebokosc.

### W34 — Glebokosc startu nie przenosi sie na potomka (kontrola do W20)

**[POTWIERDZONE]** — 2 ramiona po 30 linii.

Start ze **zwyklego** ziarna v4 vs ze **glebokiego** ziarna v14/blok A:

| pokolenie | start zwykly | start gleboki |
|---|---|---|
| 2 | 5,0 | 5,0 |
| 3 | 3,0 | 2,0 |
| **4** | **2,0** | **2,0** |
| 5 | 2,0 | 2,5 |

Zbiegaja do tego samego dna — **linia zapomina, skad wyszla.** To W20
(„liczy sie ziarno, nie operator") przeniesione o poziom wyzej i tam
**obalone**: na osi pokolen ziarno startowe nie decyduje o niczym.

### W35 — Bloki cis kosztuja glebokosc i nie zwracaja jej (zamkniecie tematu)

**[POTWIERDZONE]** — czwarty i ostatni pomiar tej osi.

Konsensus ujawnil, ze dekoder **pogarsza** sekwencje w wymiarach niewidocznych
dla Sedziego: **dokłada represor** (CreA: dziki 2 -> konsensus 4) i **usuwa
aktywator** (szeroki XBS: 3 -> 1). To bylo najlepsze uzasadnienie blokow cis,
jakie mielismy — liczone wobec naszej wlasnej bazy, nie z literatury.

`v18` = te same 100 baz co `v2` + CCAAT x4 + IR-XBS + rozbite CreA
(29–33–38 pz zmian). Zmierzony koszt:

```
blad_odtworzenia   przed  0 - 1,0 -  2
                   po     4 - 6,0 - 11      koszt +5,0
bramka             34/40 przechodzi
```

**Znacznik w rankingu nie drgnal** — `v18` jest gorszy od `v2`.
Razem z `v8`, `v12` i `v13` to **cztery** pomiary tej osi, ostatni z czysta
kontrola (jedyna zmienna = bloki). **Temat CCAAT/XBS zamkniety.**

### W36 — Znacznik czasu w /ranking jako jedyny odczyt surowego wyniku

**[POTWIERDZONE]** — metoda, nie wynik, ale bez niej trzy powyzsze wnioski
byłyby nieodczytywalne.

Serwer trzyma **najlepsze** zgloszenie po **surowym** TOP10. Potwierdzone
dwukrotnie w tej sesji: `v18` (17:50) i `v19` (20:08) nie ruszyly znacznika
`17:34:45`. Zatem znacznik sie rusza wtedy i tylko wtedy, gdy nowy plik ma
wyzszy surowy TOP10.

> **Pulapka, w ktora wpadlismy.** `v2` dal „tyle samo punktow co v14" i zostal
> odczytany jako porazka. W rzeczywistosci **znacznik przesunal sie z 16:52:28
> na 17:34:45** — surowy wynik wzrosl. Rownoczesnie trzy druzyny wgraly lepsze
> pliki, wiec nasza *ranga* spadla. Punkty z roznych godzin nie sa
> porownywalne; znacznik jest.
