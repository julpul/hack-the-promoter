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

