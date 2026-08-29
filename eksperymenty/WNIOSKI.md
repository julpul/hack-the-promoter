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
| 1 | `runs/julian/pula.fasta` | `hybryda`: 1 z mapy + 49 z `/edycje` + 50 krzyżówek | **1** | 2 | 17,5 | jednorodna pula — wysoka średnia, brak ogona (W8) |
| 2 | | | | | | |

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

