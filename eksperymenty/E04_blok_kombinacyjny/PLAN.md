# E04 · Plan faktorialny 2⁴ — gatunek × CreA × rdzeń × tło

**Status:** [OTWARTE] · **Zależy od:** E01 (selekcja), E02 (czynnik C), E03 (treść rdzenia) · **Koszt:** ~200 wywołań, 10 min

---

## Luka, którą to zamyka

Plan zgłoszenia z fazy 1 (komórka 36 `hipotezy.ipynb`):

```
~30  wariant gatunkowy + okolica
~30  dekoder + ręczna edycja rdzenia
~20  TATAAA w oknie 720-770
~10  rozbite CreA
~10  zwycięzcy hybrydy
```

Pięć bloków, każdy testuje **jedną** zmianę. Ani jedna sekwencja nie łączy dwóch.
Tymczasem pozycje, na które działają te hipotezy, są **rozłączne**:

| czynnik | pozycje | źródło |
|---|---|---|
| **A** gatunek | 154, 287, 362, 430, 434, 648, 750, 754, 778 (+ 276 w iteracji 2) | `zmien_na`, H7 |
| **B** CreA | 560–565 | skan IUPAC `SYGGRG` |
| **C** rdzeń | 783–800 | `wagaP` > 0,5, H1 |
| **D** tło | wszystkie pozostałe | dziki albo wyjście `/edycje` |

Rozłączność znaczy, że edycje **się nie znoszą** i dają się złożyć w jednej
sekwencji. Jeśli każdy efekt jest choćby lekko dodatni, kombinacja jest
najsilniejszym kandydatem w całej puli — a w obecnym planie nie ma jej wcale.

Do tego plan faktorialny daje coś, czego pięć osobnych bloków nie daje:
**efekty główne i interakcje z tej samej liczby sekwencji**. To jest różnica
między „zmieniliśmy kilka rzeczy i wyszło lepiej" a odpowiedzią na pytanie
Jury „skąd wiecie, który składnik działa".

## Czynniki

### A — dopasowanie gatunkowe (0/1)
`0` = bez zmian. `1` = `zastosuj_rekomendacje` iterowane do punktu stałego
(2 iteracje, ~10 zmian — H7).

**Uzasadnienie biologiczne:** kanał gatunku dopasowuje sekwencję do preferencji
*T. atroviride* P1 — użycie kodonów regionu, kontekst nukleotydowy miejsc
wiązania, skład lokalny. Wyrocznia ocenia w kontekście tego szczepu.

**Uwaga:** wariant A=1 **przegrywa z dzikim u Sędziego**. To jest oczekiwane
(sekcja 4.2 briefu, W7) i nie jest powodem do odrzucenia. Sędzia nie widzi
gatunku, więc karze za specjalizację.

### B — rozbicie miejsca CreA (0/1)
`0` = bez zmian. `1` = zniszczenie motywu `SYGGRG` na poz. 560.

**Uzasadnienie biologiczne:** CreA to represor represji katabolicznej węglem.
Na glukozie wiąże się i wycisza gen. Rozbicie miejsca **usuwa hamulec** zamiast
dodawać gaz — działa w wymiarze, którego Sędzia z definicji nie mierzy
(on porównuje „promotorowatość", nie derepresję).

Konkretnie: `SYGGRG` = `[GC][CT]GG[AG]G`. Niezmienne są dwie G na pozycjach
3–4 motywu. Podmiana `GG` → `TT` na poz. 562–563 niszczy rdzeń miejsca
wiązania przy minimalnej liczbie zmian. Wariant zapasowy: podmiana całych
sześciu pozycji na sekwencję o tym samym GC.

### C — zaprojektowany rdzeń (0/1)
`0` = rdzeń jak w rodzicu. `1` = okno 783–800 nadpisane **po dekodowaniu**.

**Warunkowe:** ten czynnik wchodzi tylko jeśli E02 orzeknie BIOLOGIA lub
CZĘŚCIOWY. Jeśli ARTEFAKT — `run.py` sam go wycina i plan schodzi do 2³.

**Treść:** priorytetowo konsensus z E03 (18 pz wyprowadzone ze stu naturalnych
promotorów *Trichoderma* wyrównanych do TSS). Zapasowo, jeśli E03 nie
uruchomione: wariant z elementem Inr-podobnym.

**Krytyczne:** nadpisanie musi być **ostatnim** krokiem. Z 18 pozycji rdzenia
**16 ma `rekon=1`**, czyli odtwarzają się z samych kodów — przepuszczenie
sekwencji przez enkoder-dekoder je regeneruje. Trzy z nich (784, 788, 792) mają
do tego zero dźwigni, więc dekoder wypisuje je ze swojego prioru **niezależnie
od kodów** i nie da się ich ruszyć żadną edycją latentu. Swobodne są tylko dwie:
790 i 798. Kolejność to zawsze `/edycje` → ręczna edycja, nigdy odwrotnie.

### D — tło (0/1)
`0` = dziki jako podkład. `1` = wyjście `/nawigator/edycje` (poziom 2,
`ile_kodow` 8) — czyli sekwencja na rozmaitości prototypów.

**Po co:** rozdziela „bycie prototypem dekodera" (co Sędzia nagradza — W4)
od trzech edycji celowanych. Jeśli D ma duży efekt główny, a A/B/C małe,
to znaczy, że nasz wynik z pierwszego zgłoszenia brał się wyłącznie z bycia
prototypem — i to jest odpowiedź na pytanie o rozjazd proxy z sekcji 6 briefu.

## Plan

16 komórek (2⁴) × 3 repliki = **48 sekwencji**. Repliki różnią się ziarnem
`/edycje` dla D=1 i ziarnem wypełniacza dla B=1, więc replika mierzy wariancję
wykonania, nie wariancję hipotezy.

Etykiety: `E04_A1B0C1D1_r02` — czynniki wprost w nazwie, więc po zgłoszeniu
widać skład portfela bez sięgania do notatek.

## Pomiar

Dla każdej z 48 sekwencji:

1. `mapa()` → metryki nagłówka. Jeśli E01 dał scorer — to jest **zmienna
   zależna** i można policzyć efekty główne zwykłą regresją.
2. `lepsza(dziki, kandydat)` → bramka, nie miara. Zapisujemy, ale **nie
   odrzucamy** na tej podstawie (W4, W7).
3. `lepsza(rodzic, kandydat)` — porównanie z własnym tłem, żeby rozdzielić
   efekt edycji od efektu tła.

## Analiza

Efekt główny czynnika X przy zmiennej zależnej *y*:

```
efekt(X) = średnia(y | X=1) − średnia(y | X=0)
```

Interakcja AB:

```
int(A,B) = [ y(A1B1) − y(A1B0) ] − [ y(A0B1) − y(A0B0) ]
```

Przy 3 replikach i 8 komórkach na poziom czynnika przedziały będą szerokie.
**To jest eksploracja, nie test istotności** — i tak trzeba to opisać.
Interakcja warta uwagi to taka, która przekracza rozstęp replik.

## Kryteria decyzyjne

| obserwacja | konsekwencja dla portfela E05 |
|---|---|
| efekt A dodatni | blok gatunkowy rośnie; A=1 wchodzi do bazy większości bloków |
| efekt B dodatni | CreA wchodzi jako domyślna warstwa, nie osobny blok |
| efekt C dodatni | rdzeń jako druga domyślna warstwa; potwierdza E02 drugim torem |
| efekt D >> A,B,C | **ostrzeżenie**: wygrywamy prototypowością, nie biologią; podnieść udział zakładów spoza rozmaitości |
| jakakolwiek silna interakcja | ta kombinacja dostaje własny blok i największą liczbę sztuk |
| wszystkie efekty ≈ 0 | scorer nie rozdziela (patrz E01) — przejść na czystą różnorodność |

## Wykresy do notebooka

1. **Efekty główne** — cztery panele, `y` vs poziom czynnika, z punktami replik.
2. **Macierz interakcji** — heatmapa 4×4 wielkości interakcji parowych.
3. **Wykres 16 komórek** — posortowane średnie, etykiety `A1B0C1D1`,
   dziki jako linia odniesienia. To jest ranking kombinacji.
4. **Zgodność scorera z Sędzią** — dla każdej komórki: wartość scorera vs
   odsetek wygranych u Sędziego. Punkty odstające to udokumentowany rozjazd proxy.

## Zastrzeżenia

- 3 repliki na komórkę to mało. Efekty poniżej rozstępu replik są szumem.
- Zmienna zależna jest proxy (metryka Nawigatora), nie oceną Wyroczni.
- Czynniki mogą nie być addytywne w sensie biologicznym, nawet jeśli pozycje
  są rozłączne — na przykład edycja rdzenia może zmieniać kontekst, w którym
  działa derepresja CreA.
- Ten plan mierzy efekty **w metryce modelu**. Zdanie „efekt B jest dodatni"
  znaczy „Nawigator ocenia sekwencje z rozbitym CreA wyżej", nie „derepresja
  zwiększa ekspresję w komórce".

## Uruchomienie

```bash
python eksperymenty/E04_blok_kombinacyjny/run.py            # pelne 2^4
python eksperymenty/E04_blok_kombinacyjny/run.py --bez-c    # gdy E02 = ARTEFAKT
python eksperymenty/E04_blok_kombinacyjny/run.py --replik 5
```

Wyjściem jest `wyniki.json` **oraz** `kandydaci.fasta` — 48 sekwencji gotowych
do wciągnięcia do portfela w E05.
