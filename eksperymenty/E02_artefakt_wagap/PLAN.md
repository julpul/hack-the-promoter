# E02 · Czy szczyt `wagaP` to rdzeń promotora, czy artefakt brzegowy?

**Status:** [OTWARTE] · **Blokuje:** 30 sekwencji planu zgłoszenia · **Koszt:** ~30 wywołań, 1 min

---

## Dlaczego trzeba to zrobić przed zgłoszeniem

H1 zmierzyła, że 32,4 % masy gradientu siedzi w 2,2 % długości sekwencji
(okno 783–800), a mediana `wagaP` w reszcie to 0,034. Faza 1 zinterpretowała
to jako rdzeń promotora przy miejscu startu transkrypcji i na tej podstawie
plan zgłoszenia (komórka 36) przeznaczył **30 ze 100 sekwencji** na edycję
tego okna.

Sam notebook w komórce 6 zapisał uczciwe zastrzeżenie:

> Alternatywne wyjaśnienie to **artefakt brzegowy**: sieci konwolucyjne bywają
> wrażliwe na krawędź wejścia. Nie rozstrzygnęliśmy tego.

Nie rozstrzygnięto, a mimo to zbudowano na tym 30 % budżetu. To jest dokładnie
ten sam błąd, co w sekcji 4.2 briefu (odrzucenie edycji gatunkowych na podstawie
modelu, który gatunku nie widzi) — wniosek wyciągnięty szybciej, niż pozwalał
pomiar.

## Jak to rozstrzygnąć

Trzeba rozdzielić dwie rzeczy, które w dzikim promotorze są ze sobą sklejone:
**treść** okna 783–800 i **pozycję** okna 783–800.

| przekształcenie | treść | pozycja | co mówi |
|---|---|---|---|
| **rotacja o *k*** | zachowana w całości | przesunięta o *k* | **rozstrzygające** |
| odwrócenie | zachowana, kolejność odwrócona | lustrzana | wspiera rotację |
| permutacja | zniszczona | — | kontrola: sygnał bez treści |
| losowa o GC dzikiego | brak | — | kontrola zerowa |
| dziki z rdzeniem zastąpionym losowo | zniszczona **tylko w oknie** | zachowana | test lokalny |
| naturalne promotory | inna, ale prawdziwa | wyrównana do TSS | test biologiczny |

**Rotacja jest kluczowa**, bo zachowuje każdy lokalny motyw i cały kontekst
sąsiedztwa — zmienia wyłącznie odległość od krawędzi wejścia. Jeśli w
`obroc(dziki, 400)` szczyt wyląduje w okolicy pozycji 383 (tam trafia
oryginalne 783), sygnał idzie za treścią. Jeśli zostanie na 783–800,
model patrzy na krawędź, nie na promotor.

Główną metryką jest **środek masy rozkładu `wagaP`** (`wspolne/metryki.py`).
To jeden skalar, iloraz wielkości znormalizowanych tak samo, więc normalizacja
min-max się skraca i wolno go porównywać między sekwencjami. Dla rozkładu
płaskiego wynosi ~400,5; dla dzikiego jest silnie przesunięty w prawo.

## Hipotezy

| # | hipoteza | predykcja jeśli **BIOLOGIA** | predykcja jeśli **ARTEFAKT** |
|---|---|---|---|
| **E02.1** | rotacja przesuwa szczyt | środek masy wędruje razem z treścią | środek masy zostaje ~795 dla każdego *k* |
| **E02.2** | permutacja niszczy szczyt | rozkład płaski, środek masy ~400 | szczyt dalej na końcu |
| **E02.3** | sekwencja losowa nie ma szczytu | rozkład płaski | szczyt dalej na końcu |
| **E02.4** | zniszczenie samego rdzenia zmienia rozkład | masa rdzenia spada | bez zmian |
| **E02.5** | naturalne promotory mają szczyt w tym samym miejscu | tak — wszystkie wyrównane do TSS | tak, ale to nic nie znaczy |

**E02.5 nie rozstrzyga sama z siebie** i trzeba to jasno powiedzieć: naturalne
promotory też są wyrównane do TSS, więc szczyt na końcu jest zgodny z obiema
hipotezami. Wchodzi do eksperymentu jako materiał dla E03 i E04, nie jako dowód.

Uwaga na szew rotacji: `obroc` skleja koniec z początkiem, więc powstaje jedno
sztuczne złączenie. Przy *k* = 100, 200, 400, 600 szew ląduje w różnych
miejscach, więc efekt szwu nie może udawać systematycznego trendu.

## Bateria (24)

```
dziki                              1
rotacje k = 100, 200, 400, 600     4      <- rozstrzygające
odwrocony                          1
przetasowane, 3 ziarna             3
losowe o GC dzikiego, 3 ziarna     3
dziki z rdzeniem 783-800 losowym   2
dziki z rdzeniem = poli-A          1      <- skrajny przypadek
naturalne z promotory_100.csv     10      <- rozkład szczytów w prawdziwych promotorach
```

## Kryteria decyzyjne

| obserwacja | werdykt | konsekwencja |
|---|---|---|
| środek masy rotacji przesuwa się o ≈ *k* | **BIOLOGIA** | czynnik C w E04 zostaje; blok rdzeniowy w portfelu zostaje; mamy mocny slajd |
| środek masy zostaje > 700 dla każdej rotacji **i** dla permutacji **i** dla losowej | **ARTEFAKT** | wyciąć czynnik C z E04; przenieść 30 sekwencji na H7 + CreA + chimery z E03 |
| mieszany (rotacja przesuwa, ale permutacja też ma szczyt) | **CZĘŚCIOWY** | jest składowa pozycyjna i składowa treściowa; edytować rdzeń, ale nie wiązać z nim więcej niż 15 sekwencji |

## Wykresy do notebooka

1. **Nakładka profili `wagaP`** — dziki i cztery rotacje na jednym wykresie,
   z pionowymi liniami tam, gdzie *powinien* wylądować szczyt przy każdej
   rotacji. Jeden rzut oka i jest werdykt.
2. **Środek masy vs rotacja** — punkty zmierzone, na tle dwóch linii
   przewidywanych: „idzie za treścią" (nachylenie −1) i „zostaje na krawędzi"
   (pozioma). To jest wykres na slajd.
3. **Profile kontrolne** — permutacja, losowa, rdzeń zniszczony, w siatce.
4. **Rozkład `argmax` w 10 naturalnych promotorach** — histogram pozycji
   maksimum. Jeśli wszystkie na końcu, opisać ostrożnie (patrz E02.5).

## Zastrzeżenia

- Rotacja tworzy szew; jeden na sekwencję, w różnych miejscach dla różnych *k*.
- Model mógł być trenowany wyłącznie na sekwencjach wyrównanych do TSS,
  więc rotacja daje mu wejście spoza rozkładu treningowego. Zachowanie poza
  rozkładem nie musi być informatywne — dlatego permutacja i losowa są
  potrzebne jako drugi, niezależny tor kontroli.
- Werdykt „artefakt" **nie** znaczy, że okno 783–800 jest biologicznie
  nieważne. Znaczy tylko, że `wagaP` nie jest dowodem na jego ważność.
  Rdzeń promotora przy TSS ma niezależne uzasadnienie z literatury.

## Uruchomienie

```bash
python eksperymenty/E02_artefakt_wagap/run.py
```
