# E03 · Naturalne promotory jako drugi punkt startowy i źródło motywów

**Status:** [OTWARTE] · **Zasila:** E04, E05 · **Koszt:** ~300 wywołań, 5 min

---

## Dlaczego dopiero teraz

Otwarte pytanie 4 z briefu badawczego: *„Czy naturalne promotory z
`promotory_100.csv` biją dzikiego?"*. Nigdy nie sprawdzone, bo pliku nie było
w `data/`. Teraz jest.

To jedyny w całym projekcie zbiór sekwencji, który **nie pochodzi z modelu**.
Wszystko inne — pula `hybryda`, wyjścia `/edycje`, warianty gatunkowe — to
wytwory Nawigatora oceniane przez Sędziego. Analizowanie tego zbioru i szukanie
w nim korelacji to badanie własnego generatora, nie biologii. Sto naturalnych
promotorów z dziewiętnastu gatunków *Trichoderma* przerywa tę pętlę.

> **Nie mylić z sekwencjami „silnych promotorów" krążącymi w zespole.** Tamte
> (Ptef1, PcDNA1, Ppdc1, PgpdA, Pcbh1, Pnag1, Pxyn2 z modelu językowego) to
> tandemowe powtórzenie `AGCTAGCTAGCTAGG` o okresie 48 pz, 840 pz długości
> i entropii 4-merów 2,89 bita. Patrz W13 w `WNIOSKI.md`. Nie wchodzą tu ani
> jako dane, ani jako kontrola pozytywna.

## Cztery rzeczy do wyciągnięcia

### 1. Drugi punkt startowy
Czy któryś naturalny promotor bije dzikiego u Sędziego? Jeśli tak, mamy drugą
bazę do `/edycje` i drugie centrum portfela — a to bezpośrednio zwiększa liczbę
**niezależnych** losowań w ogonie (W11).

### 2. Konsensus rdzenia (zasila czynnik C w E04)
Obecny plan wstawia w okno 783–800 motywy z podręcznika (`TATAAA`, `CCAAT`).
Konsensus ostatnich 18 pz stu naturalnych promotorów *Trichoderma*
wyrównanych do TSS jest o klasę lepszym uzasadnieniem — i przed Jury broni się
sam. To zamienia czynnik C z „wstawiliśmy TATA-box" w „wstawiliśmy element
rdzeniowy wyprowadzony ze stu naturalnych promotorów rodzaju".

### 3. Archetypy (zasilają bloki portfela w E05)
Klastrowanie po profilu k-merów. Oczekiwane rozdzielenie na promotory
konstytutywne glikolityczne (wysokie GC, silne elementy rdzeniowe) i
indukowalne CAZyme/mykopasożytnicze (miejsca wiązania czynników
specyficznych). Każdy klaster = jedna niezależna hipoteza = jeden blok w portfelu.

### 4. Materiał na chimery
Krzyżówki dziki × naturalny, z punktem cięcia dobranym tak, żeby rdzeń
pochodził od jednego rodzica, a reszta od drugiego. To najtańszy sposób
na sekwencje daleko od rozmaitości dekodera, a jednocześnie **złożone
wyłącznie z prawdziwego DNA** — czyli dokładnie odwrotność losowej mutacji,
która nie działa (W5).

## Uwaga metodologiczna: te promotory nie są etykietowane siłą

`data/README.md` mówi wprost: *„to nie jest zestaw dobrych odpowiedzi, tylko
materiał porównawczy"*. Nie wiadomo, które są silne. Więc:

- **wolno**: opisywać ich strukturę, liczyć konsensus, klastrować, używać
  jako materiału do chimer, sprawdzać werdykt Sędziego;
- **nie wolno**: nazywać ich „silnymi promotorami" i mówić, że korelacje
  w nich znalezione opisują siłę.

Jeśli zostanie czas, etykiety siły dałoby się dołożyć z danych ekspresyjnych
mRNA-seq z NCBI (osobny, opcjonalny kierunek — patrz `E06_mrna_seq/PLAN.md`,
jeśli powstanie). To jedyna droga do korelacji „sekwencja ↔ siła" opartej na
pomiarze mokrym, a nie na modelu.

## Protokół

1. Wczytaj `data/promotory_100.csv`, doprowadź do 800 pz kotwicząc **koniec 3'**
   (promotory są wyrównane do TSS — to koniec jest punktem odniesienia).
   Zapisz oryginalne długości; jeśli trzeba było dopełniać `N`, odnotować.
2. Dla każdego: `lepsza(dziki, naturalny)` → kto bije dzikiego.
3. Dla każdego: `mapa()` → metryki nagłówka (jeśli E01 dał scorer, to jest
   ranking siły niezależny od Sędziego).
4. Offline: skan motywów IUPAC, GC, skład, profil k-merów (k = 4), konsensus
   pozycyjny okna 783–800 i okna −80…−30 (poz. 720–770).
5. Offline: PCA na profilach 4-merów + k-means. Bez `sklearn` — SVD z `numpy`
   i k-means w kilkunastu linijkach wystarczą, a repo zostaje bez zależności.
6. Chimery: dla 5 najlepszych naturalnych zbuduj krzyżówki z dzikim
   (cięcie przed rdzeniem, za rdzeniem, w połowie) i sprawdź u Sędziego.

## Kryteria decyzyjne

| obserwacja | konsekwencja |
|---|---|
| ≥ 1 naturalny bije dzikiego | drugi punkt startowy; osobny blok w portfelu; `/edycje` od niego |
| żaden nie bije | spodziewane (Sędzia lubi prototypy, a naturalne są „pojedynczymi próbkami"); nadal używamy ich jako materiału na chimery i konsensus |
| konsensus rdzenia różny od dzikiego | czynnik C w E04 dostaje treść wyprowadzoną z danych |
| klastry rozdzielają się czytelnie | bloki portfela po archetypach |
| chimery biją dzikiego | najtańsza droga do ogona TOP10 — zwiększyć ich udział |

## Wykresy do notebooka

1. **Ile bije dzikiego** — słupek + rozkład dystansów Hamminga naturalnych
   od dzikiego (spodziewane: ~600, czyli zupełnie inne sekwencje).
2. **Logo pozycyjne okna 783–800** — częstości zasad na 18 pozycjach,
   dziki nałożony jako linia. Bezpośrednio pokazuje, co wstawiać w czynniku C.
3. **PCA profili 4-merów** — punkty pokolorowane klastrem, dziki zaznaczony
   krzyżykiem. Pokazuje, czy dziki leży wewnątrz chmury naturalnych, czy na
   jej brzegu.
4. **Mapa motywów** — obecność TATA / CAAT / GC-box / CreA w każdym promotorze
   jako heatmapa, posortowana klastrem.
5. **Metryki nagłówka naturalnych vs dziki vs pula `hybryda`** — jeśli E01 dał
   scorer, to jest najciekawszy wykres: gdzie na osi leżą prawdziwe promotory
   względem naszych wytworów dekodera.

Wykres 5 jest wart osobnej uwagi. Jeśli nasza pula ma **lepszy** wynik niż
wszystkie sto naturalnych promotorów, to jest to podręcznikowy objaw rozjazdu
proxy: wyprodukowaliśmy coś, co model lubi bardziej niż prawdziwe DNA.
Sekcja 6 briefu ostrzega dokładnie przed tym i taki wykres jest gotowym slajdem.

## Uruchomienie

```bash
# najpierw wrzuc plik z materialow hackathonu:
cp <sciezka>/promotory_100.csv data/promotory_100.csv
python eksperymenty/E03_naturalne_promotory/run.py
```
