# E01 · Czy nagłówek `/mapa` zawiera funkcję celu?

**Status:** [OTWARTE] · **Blokuje:** E04, E05 · **Koszt:** ~60 wywołań, 2 min

---

## Dlaczego to jest najważniejszy eksperyment fazy 2

Faza 1 skończyła się tabelą (komórka 29 `hipotezy.ipynb`):

| chciałbyś | masz |
|---|---|
| funkcję straty *L(x)* | komparator „a czy b" |
| gradient ∇*L* | `wagaP` = moduł gradientu |
| czuły pomiar | próg czułości (H4/H5) |

Cała reszta wynikała z pierwszego wiersza. Wspinaczka padła (H6), bo kryterium
było wysycone. Selekcja puli jest niemożliwa, bo nie ma czego sortować.
Porównywanie hipotez wymaga zużycia okna 5 minut i daje ~1 bit.

**Ale ten pierwszy wiersz może być nieprawdziwy.**

Legenda API zastrzega nieporównywalność między sekwencjami **wyłącznie dla
`wagaP`**. W tym samym nagłówku siedzą cztery pola, których to zastrzeżenie
nie dotyczy:

```
zmian_pod_gatunek    9        ile pozycji kanał gatunku chce jeszcze zmienić pod P1
blad_odtworzenia    80        bezwzględny błąd rekonstrukcji tej sekwencji
nie_rekonstruuje    89        ile pozycji nie odtwarza się z samych kodów
rekon_frakcja    0.8888       udział pozycji odtwarzanych
```

To są **bezwzględne liczby całkowite**, nie normalizowane w obrębie sekwencji.
Jeśli wariują między sekwencjami, mamy skalar.

Najciekawszy jest `zmian_pod_gatunek`. To licznik niedopasowania do szczepu P1,
malejący 9 → 1 → 0 w H7. Trzy argumenty, dlaczego akurat on:

- **jest bezwzględny** — liczba pozycji, nie ranga wewnątrz sekwencji;
- **nie jest wysycony** — H4/H6 pokazały wysycenie Sędziego, nie tego kanału;
- **mierzy właściwą oś** — Wyrocznia ocenia w kontekście `pks1` i P1;
  Sędzia gatunku nie widzi, a ten kanał widzi tylko gatunek.

`blad_odtworzenia` mierzy co innego i jest komplementarny: jak daleko
sekwencja leży od rozmaitości promotorów wyuczonej przez autoenkoder.
Niższy = model „rozpoznaje" sekwencję lepiej. To jest ciągła wersja tego, co
Sędzia mówi binarnie i z wysyceniem.

## Hipotezy

| # | hipoteza | jak obalić |
|---|---|---|
| **E01.1** | `blad_odtworzenia` wariuje między sekwencjami | odchylenie standardowe = 0 na baterii 28 sekwencji |
| **E01.2** | `zmian_pod_gatunek` wariuje między sekwencjami | j.w. |
| **E01.3** | Oba są **deterministyczne** (ta sama sekwencja → ta sama liczba) | 5 powtórzeń dla dzikiego daje różne wartości |
| **E01.4** | `blad_odtworzenia` koreluje z werdyktem Sędziego | brak różnicy median między wygranymi a przegranymi |
| **E01.5** | `zmian_pod_gatunek` **nie** koreluje z werdyktem Sędziego | *odwrotnie niż wyżej* — tu **brak** korelacji potwierdza hipotezę, bo Sędzia nie widzi gatunku (patrz niżej) |

E01.5 jest sformułowana odwrotnie celowo. Jeśli `zmian_pod_gatunek` jest osią
niewidoczną dla Sędziego, to jego **niezależność** od werdyktu Sędziego jest
potwierdzeniem, a nie porażką. Dwa proxy warto mieć wtedy, gdy mierzą różne
rzeczy — skorelowane proxy nie wnosi informacji.

## Bateria sekwencji (28)

Dobrana tak, żeby rozpiąć jak najszerszy zakres „odległości od dzikiego"
i jak najwięcej **rodzajów** odległości.

| grupa | ile | po co |
|---|---|---|
| dziki | 1 | punkt odniesienia |
| dziki, 5 powtórzeń wywołania | 4 | test determinizmu (E01.3) |
| wariant gatunkowy, iteracja 1 i 2 | 2 | znane punkty na osi `zmian_pod_gatunek` (9 → 1 → 0) |
| z istniejącej puli `hybryda` | 8 | realne kandydatki, ~100 zmian |
| z `/edycje`, poziomy 0/1/2 | 6 | wyjścia dekodera, różne poziomy latentu |
| losowe podstawienia (5, 50, 200 zmian) | 3 | znane, uporządkowane pogorszenie — **kontrola monotoniczności** |
| dziki przetasowany | 1 | ten sam skład, zero struktury — dolna granica |
| losowa o GC dzikiego | 1 | kontrola zerowa |
| naturalne z `promotory_100.csv` | 2 | inne prawdziwe promotory |

Grupa „losowe podstawienia" jest kluczowa: znamy uporządkowanie *a priori*
(5 zmian jest bliżej dzikiego niż 200). Jeśli metryka nie odtworzy tego
uporządkowania, nie jest miarą niczego użytecznego, choćby i wariowała.

## Protokół

1. Zbuduj baterię (deterministycznie, ziarna zapisane w `wyniki.json`).
2. Dla każdej: `mapa()` → `metryki_mapy()`.
3. Dla każdej (poza powtórzeniami): `lepsza(dziki, kandydat)` → werdykt Sędziego.
4. Zapisz wszystko do `wyniki.json` razem z sekwencjami — żeby dało się
   powtórzyć analizę bez ponownych wywołań.

## Kryteria decyzyjne

Wypełnić w `WNIOSKI.md` po uruchomieniu.

| warunek | werdykt | co robimy dalej |
|---|---|---|
| odch. std `blad_odtworzenia` > 2 **i** deterministyczne **i** monotoniczne na grupie kontrolnej | **mamy scorer** | E04 selekcjonuje nim komórki; E05 sortuje nim pulę; wraca wspinaczka z W6 |
| wariuje, ale nie jest monotoniczne na kontroli | **ostrożnie** | używać tylko do odsiewania skrajności, nie do rankingu |
| odch. std ≈ 0 albo niedeterministyczne | **brak scorera** | scenariusz SUCHY / RDZEŃ z drzewa decyzyjnego w README |
| `zmian_pod_gatunek` wariuje i jest **nieskorelowany** z Sędzią | **drugie proxy** | osobna oś w E04; warianty gatunkowe wchodzą do puli mimo przegranej u Sędziego |

## Wykresy do notebooka

1. **Rozrzut metryk po grupach** — stripplot `blad_odtworzenia` i
   `zmian_pod_gatunek` z grupą na osi X. Natychmiast widać, czy jest wariancja.
2. **Monotoniczność na kontroli** — `blad_odtworzenia` vs liczba losowych
   podstawień (5/50/200) plus dziki i przetasowany jako punkty skrajne.
3. **Metryka vs werdykt Sędziego** — boxplot rozdzielony na wygrane/przegrane,
   dla obu metryk. Rozdzielenie dla `blad_odtworzenia`, brak rozdzielenia dla
   `zmian_pod_gatunek` = najlepszy możliwy wynik (dwa niezależne proxy).
4. **Macierz korelacji Spearmana** wszystkich metryk nagłówka + `masa_rdzenia`
   + dystans Hamminga od dzikiego. Pokazuje, które pola są redundantne.

## Zastrzeżenia, które trzeba wypowiedzieć przy Jury

- Determinizm sprawdzony na jednej sekwencji × 5 powtórzeń. Model może być
  deterministyczny lokalnie i niedeterministyczny przy większym obciążeniu GPU.
- Korelacja z Sędzią nie jest walidacją względem Wyroczni. Oba są proxy.
  Prawdziwym testem jest ranking po wgraniu, a on niesie ~1 bit.
- Niski `blad_odtworzenia` znaczy „blisko rozmaitości modelu", a nie „silny
  promotor". To ten sam typ pomyłki, który sekcja 6 briefu nazywa prawem
  Goodharta — z tą różnicą, że tutaj wiemy o tym z góry.

## Uruchomienie

```bash
python eksperymenty/E01_funkcja_celu/run.py
# wyniki -> eksperymenty/E01_funkcja_celu/wyniki.json
```

Bez `data/promotory_100.csv` eksperyment zadziała, tylko pominie 2 sekwencje
naturalne (wypisze ostrzeżenie).
