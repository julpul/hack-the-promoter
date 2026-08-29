# Brief badawczy: Hack the Promoter

Dokument dla modelu pracującego w trybie research. Zawiera **stan wiedzy zmierzony
empirycznie** na dzień 2026-08-29, opis każdego narzędzia z jego ograniczeniami
oraz listę otwartych pytań.

Rozróżnienie w całym dokumencie:
**[ZMIERZONE]** = wynik faktycznego wywołania API, liczby są prawdziwe.
**[Z DOKUMENTACJI]** = podane przez organizatorów lub legendę API.
**[HIPOTEZA]** = interpretacja, niezweryfikowana.

---

## 1. Zadanie

Zaprojektować promotor dla genu `pks1` (biosynteza 6PP) w *Trichoderma atroviride*
szczep P1, kategoria: antagonizm biotyczny. Zgłoszenie = plik FASTA ze **100
sekwencjami po 800 pz**.

### Twarde ograniczenia [Z DOKUMENTACJI, potwierdzone przez serwer]

Każda sekwencja musi mieć **dokładnie 800 pz**, składać się ze znaków `ACGTN`,
zawierać **≤ 10 % `N`** (czyli ≤ 80 z 800) i być **unikalna w pliku**.
Oceniane jest pierwsze 100 sekwencji po filtrach. Nadmiar jest ignorowany.

Uzasadnienie progu `N`: pozycja `N` wchodzi do modelu jako 0,25 w każdym z czterech
kanałów one-hot, a nie 1,0 w jednym. Gęsta w `N` sekwencja karmi model rozkładem
spoza treningu.

### Punktacja [Z DOKUMENTACJI + ZMIERZONE]

- `TOP10` = suma 10 najlepszych / **10** (dzielnik stały)
- `ALL100` = suma wszystkich / **100** (dzielnik stały)
- Brakujące sekwencje wchodzą **jako zera** — dlatego zawsze wysyłamy pełne 100.
- Obie kategorie przeliczane rangowo wśród drużyn, które cokolwiek wgrały:
  `punkty = 10 × (N_startujących − pozycja) / (N_startujących − 1)`.
  [ZMIERZONE: przy 5 startujących skala to 10 / 7,5 / 5 / 2,5 / 0.]
- Każda kategoria to 25 % oceny końcowej, pozostałe 50 % to prezentacja przed Jury.
- **Serwer wybiera najlepsze zgłoszenie drużyny po TOP10**, nie po sumie punktów
  (pole `uwaga` w odpowiedzi `/wgraj`). To czyni TOP10 kategorią priorytetową.
- Remis rozstrzyga wcześniejsza data wgrania.

---

## 2. Trzy modele, dwa dostępne

| model | dostęp | zwraca | zakres rozumienia |
|---|---|---|---|
| **Sędzia** | tak | dla pary: która silniejsza | **wąski**: tylko „co jest promotorem" / „który bardziej promotorowy" |
| **Nawigator** | tak | mapa pozycji + propozycje edycji | **szeroki**: odpowiada z kontekstu biologicznego |
| **Wyrocznia** | **nie** | ocena punktowa zgłoszeń | zna kontekst genu `pks1` |

[Z DOKUMENTACJI, przekazane przez organizatorów 2026-08-29]
Sędzia wie w zasadzie tylko tyle, **który z pary jest silniejszym promotorem albo
co w ogóle jest promotorem**. Nawigator ma **istotnie szerszy obszar rozumienia
biologicznego**.

Żadne dostępne narzędzie nie zwraca liczby. Jedyny sygnał od Wyroczni to pozycja
w rankingu po wgraniu — czyli **dwie liczby zbiorcze na 5 minut**, bez atrybucji
do pojedynczych sekwencji.

### 2.1 Konsekwencja: podział ról między narzędziami

To przeformułowuje całą strategię i tłumaczy pomiary z sekcji 4.

**Sędzia jest bramką, nie funkcją celu.** Jego oś dyskryminacji to
„promotorowatość", nie siła dla konkretnego genu. [HIPOTEZA, spójna z 4.4 i 4.5]
Dlatego nie rozdziela pojedynczych podstawień: dziki *już jest* promotorem, więc
drobna zmiana nie przesuwa go po tej osi. I dlatego warianty z dekodera wygrywają
w ~40 % — dekoder produkuje **prototypy** wyuczonej rozmaitości, a prototyp jest
bardziej „promotorowy" niż dowolna pojedyncza sekwencja naturalna.

Właściwe użycie Sędziego: pytanie **„czy nadal jest to promotor / czy czegoś nie
zepsułem"**. Nie: „czy jest silniejszy dla `pks1`" — na to pytanie on nie umie
odpowiedzieć.

**Nawigator jest głównym źródłem sygnału biologicznego.** Ma kanał gatunku,
głowicę promotorową i atrybucję na poziomie pozycji (`wagaP`). Przy sprzeczności
między Nawigatorem a Sędzią **domyślnie ufamy Nawigatorowi**, bo Sędzia operuje
na uboższej osi.

**Konsekwencja metodologiczna:** eksperymenty z rozdzielczością na pojedynczą
sekwencję da się robić **wyłącznie u Sędziego**. Wgranie nie nadaje się do
testowania hipotez — nie dowiesz się, która z 100 sekwencji zadziałała.

---

## 3. Architektura Nawigatora [Z DOKUMENTACJI + ZMIERZONE]

Hierarchiczny autoenkoder z kwantyzacją wektorową. Trzy poziomy dyskretnych kodów:

| poziom | warstwa | slotów | pz/slot | alfabet |
|---|---|---|---|---|
| 0 | L1 | 50 | 16 | 4 |
| 1 | L2 | 200 | 4 | 8 |
| 2 | L3 | 400 | 2 | 4 |

Do tego **głowica promotorowa** (przewiduje siłę, udostępniona jako gradient
`wagaP`) i **kanał gatunku** (generuje rekomendacje `zmien_na`).

### `POST /nawigator/mapa` — pola odpowiedzi

Nagłówek (dla dzikiego) [ZMIERZONE]:
```
gatunek            Trichoderma atroviride P1
rekon_frakcja      0.8888
nie_rekonstruuje   89
blad_odtworzenia   80
zmian_pod_gatunek  9
rozklad_warstw     {'0': 64, '1': 609, '2': 76, '3': 51}   # ile pozycji ma 0/1/2/3 dźwignie
```

Rekord pozycji: `{"poz":1,"wej":"T","rekon":1,"warstwy":[0,0,1],"zmien_na":".","wagaP":0.004}`

Znaczenie wg **legendy zwracanej przez API** [Z DOKUMENTACJI]:

- `rekon` — `1` = pozycja odtwarza się z samych kodów, `0` = **swobodna**
- `warstwy` — `[L1,L2,L3]`, `1` = zmiana jednego kodu tego poziomu rusza tę pozycję.
  Więcej warstw = więcej dźwigni. **Zero warstw przy `rekon=1` = dekoder nadpisze
  twoją edycję.**
- `zmien_na` — zasada, na którą zmienić wejście **pod ten szczep**; `.` = bez zmiany.
  Pokazana tylko gdy kanał gatunku realnie działa na tej pozycji.
  **To jest dopasowanie gatunkowe, NIE wskazówka siły.**
- `wagaP` — *„NIE JEST PRAWDOPODOBIEŃSTWEM. Znormalizowana min-max w tej sekwencji
  waga gradientu głowicy promotorowej, okno 25 pz. **Nieporównywalna między
  sekwencjami**"*

Dźwignie w dzikim [ZMIERZONE]: L1 rusza 118 pozycji, L2 — 319, L3 — 477.
Pozycji swobodnych (`rekon=0`): **89**. Pozycji, które dekoder nadpisze
(`rekon=1`, zero warstw): **64**.

### `POST /nawigator/edycje` — parametry

`{sekwencja, poziom: 0|1|2, ile_kodow: ≥1, opcji, ziarno}`.
Podmienia losowe kody wskazanego poziomu i dekoduje. Pole `zmiany` liczone jest
wobec linii bazowej, czyli dekodowania **bez** zmiany kodów (nie wobec wejścia).
`ile_kodow=0` → HTTP 422 [ZMIERZONE].

---

## 4. Wyniki pomiarów — to jest najważniejsza część

### 4.1 Gradient głowicy promotorowej jest skrajnie skoncentrowany [ZMIERZONE]

Rozkład `wagaP` w dzikim, średnia w oknach po 100 pz:
```
  1-100: 0.037    401-500: 0.022
101-200: 0.034    501-600: 0.054
201-300: 0.038    601-700: 0.031
301-400: 0.027    701-800: 0.222   <-- całe top 40 tutaj
```
Szczyt: poz. 788 = 1,000; 789 = 0,995; 790 = 0,992 … 800 = 0,946; poz. 783 = 0,169.
**Poza oknem 783–800 gradient wynosi ~0,03.**

[HIPOTEZA] Pozycja 800 leży przy miejscu startu transkrypcji, a głowica patrzy na
rdzeń promotora. **Alternatywna hipoteza, nieodrzucona: artefakt brzegowy sieci
konwolucyjnej.** Do rozstrzygnięcia.

### 4.2 Rekomendacje gatunkowe: werdykt Sędziego jest tu NIEMIARODAJNY [ZMIERZONE + REWIZJA]

Dziewięć rekomendacji: poz. 154, 287, 362, 430, 434, 648, 750, 754, 778 —
wszystkie o `wagaP` 0,013–0,144, czyli poza oknem uwagi głowicy promotorowej.
Wariant z naniesionymi wszystkimi dziewięcioma (**`z_mapy`**) **przegrywa
z dzikim** u Sędziego.

**REWIZJA po informacji z sekcji 2.** Wcześniejszy wniosek („rekomendacje nie
poprawiają siły") **był błędny metodologicznie**. `zmien_na` to dopasowanie
**pod szczep P1**, a Sędzia nie zna gatunku — mierzy tylko promotorowatość.
Dopasowanie gatunkowe może obniżać prototypowość, a jednocześnie **podnosić
ocenę Wyroczni**, która ocenia w kontekście `pks1` i P1.

Innymi słowy: odrzuciliśmy edycje gatunkowe na podstawie werdyktu modelu, który
z definicji nie widzi gatunku. To jeden z najbardziej prawdopodobnych błędów
w dotychczasowym podejściu. **Warianty gatunkowo dopasowane należy umieścić
w puli mimo przegranej u Sędziego** i sprawdzić efekt na rankingu.

### 4.3 Pokrętło `ile_kodow` prawie nie działa [ZMIERZONE]

```
poziom warstwa slotów alfabet błądRek ile_kodow  zmian wobec dzikiego  trafia w 783-800
  0      L1      50      4      89        2         88/ 90.8/93              2.0
  0      L1      50      4      89        8         91/ 94.8/100             2.0
  1      L2     200      8      89        2         89/ 91.0/92              2.0
  1      L2     200      8      89        8         97/ 99.0/102             2.0
  2      L3     400      4      89        2         91/ 91.3/92              2.0
  2      L3     400      4      89        8         96/ 97.8/99              2.0
```

Trzy wnioski:
1. **Błąd rekonstrukcji = 89 pozycji.** Samo przejście przez enkoder-dekoder
   przepisuje 11 % zasad. To podłoga, poniżej której nie da się zejść.
2. Podmiana 8 kodów zamiast 2 dodaje ~6 realnych zmian. Wybór poziomu też prawie
   nie zmienia dystansu.
3. **Do okna 783–800 trafiają dokładnie 2 pozycje, w każdej konfiguracji.**
   Dekoder odtwarza rdzeń niemal identycznie — czyli `/edycje` **z definicji nie
   modyfikuje regionu, na który patrzy głowica promotorowa.**

### 4.4 Sędzia ma podłogę czułości [ZMIERZONE]

Skan mutacyjny — wszystkie możliwe pojedyncze podstawienia:
```
okno 783-800 (wagaP≈1,0):     0/54 bije dzikiego
kontrola 401-418 (wagaP≈0,02): 0/54 bije dzikiego
```

Miareczkowanie losowymi podstawieniami (8 wariantów na punkt):
```
zmian:   1    2    5   10   20   40   80  160  320
bije:  0/8  0/8  0/8  0/8  0/8  0/8  0/8  1/8  0/8
```

**Sędzia nie rozdziela pojedynczych podstawień.** Zachłanna wspinaczka po jednej
zasadzie jest niewykonalna. Przy remisie zwraca `a` [ZMIERZONE: `lepsza(dziki, dziki)` = False].

### 4.5 Losowe mutacje przegrywają, edycje latentu wygrywają [ZMIERZONE]

Losowe podstawienia: praktycznie nigdy nie biją dzikiego (patrz 4.4).
Sekwencje z dekodera przy ~100 zmianach: **8/20 w losowej próbce bije dzikiego**.

[HIPOTEZA, dobrze udokumentowana] Dekoder rzutuje sekwencję na rozmaitość
promotorów wyuczoną przez model. Losowa edycja spada z tej rozmaitości i jest
zawsze gorsza; edycja w latencie porusza się po niej. **Przestrzeń liter jest
bezużyteczna jako przestrzeń przeszukiwań; przestrzeń kodów jest jedyną działającą.**

### 4.6 Motywy w dzikim [ZMIERZONE, skan IUPAC]

```
TATAAA         poz. 343
TATATA         poz. 701, 703
SYGGRG (CreA)  poz. 560
CCAAT, GGGCGG, Inr-like:  brak
```
[HIPOTEZA] Brak kanonicznego TATA w oknie −80…−30 od startu (poz. ~720–770).
CreA to miejsce represji katabolicznej — potencjalny hamulec do rozbicia.
GC 47,5 %, skład A213 T207 G191 C189.

---

## 5. Co już zostało zrobione i z jakim skutkiem

Strategia `hybryda`: 1 wariant z rekomendacji mapy + 49 z `/nawigator/edycje`
(rundy 1–7, `ile_kodow` 7→13, poziom L3) + 50 krzyżówek zwycięzców Sędziego
z drobnymi mutacjami. Cała pula w paśmie 95–109 zmian wobec dzikiego.

Wynik: **ALL100 pozycja 1, TOP10 pozycja 2, razem 17,5 pkt** (remis punktowy
z inną drużyną, przegrany na czasie wgrania).

Diagnoza: pula jednorodna — wysoka średnia, brak ogona. Wszystkie warianty
różnią się w regionie o zerowym gradiencie, przy nietkniętym rdzeniu.

### Znane słabości tego podejścia

1. Każda runda `/edycje` startuje od dzikiego, nie od najlepszego wariantu —
   to próbkowanie wokół punktu, nie wspinaczka.
2. Jedno pokolenie krzyżowania zamiast iterowanej ewolucji.
3. Zero uzasadnienia biologicznego dla konkretnych edycji.
4. Region o najwyższym gradiencie nigdy nie był modyfikowany.

---

## 6. Ostrzeżenie o Sędzim — prawo Goodharta

[Z DOKUMENTACJI, przekazane przez organizatorów]
Sędzia jest starszym modelem o wąskim zakresie: rozstrzyga „co jest promotorem"
i „który z pary bardziej promotorowy".

Optymalizowanie go do wysycenia prowadzi do sekwencji naszpikowanej TATA-boxami:
maksymalnie prototypowej i biologicznie bezsensownej. Realnie taki konstrukt bywa
martwy — stłoczone miejsca wiązania konkurują ze sobą, a nadekspresja bywa
toksyczna dla komórki.

**Objaw rozjazdu widoczny już w naszych danych:** cała pula 100 sekwencji to
wyjścia dekodera, czyli prototypy. Efekt — pozycja 1 w ALL100 (każda wygląda jak
poprawny promotor) i pozycja 2 w TOP10 (żadna się nie wyróżnia). Sędzia doprowadził
nas dokładnie tam, dokąd prowadzi jego oś: do jednorodnej przeciętności powyżej progu.

Zalecenia:
- Sędzia = **bramka „czy nadal to promotor"**, nie funkcja celu do maksymalizacji;
- przy sprzeczności z Nawigatorem **ufać Nawigatorowi** (szerszy kontekst biologiczny);
- **nie odrzucać wariantów tylko dlatego, że przegrały u Sędziego** — dotyczy to
  w szczególności edycji gatunkowych (patrz 4.2);
- nie przyjmować edycji bez uzasadnienia biologicznego (Jury o to zapyta);
- utrzymywać różnorodność puli;
- **jedynym prawdziwym sygnałem jest ranking po wgraniu.**

Test rozjazdu wart wykonania: zbudować celowo przesadzoną sekwencję (kilkanaście
TATA), sprawdzić reakcję Sędziego, wysłać w puli i zobaczyć, czy ranking drgnie.
Jeśli Sędzia ją kocha, a ranking nie rośnie — mamy udokumentowany rozjazd proxy
i gotowy slajd na prezentację.

---

## 7. Otwarte pytania badawcze

1. **Czy poz. 800 to faktycznie miejsce startu transkrypcji, czy artefakt brzegowy?**
   Test: policzyć `wagaP` dla sekwencji losowej i dla naturalnych promotorów
   z `promotory_100.csv`. Jeśli szczyt zawsze na końcu niezależnie od treści —
   artefakt.
2. **Czy da się edytować okno 783–800 z pominięciem dekodera?** Weź sekwencję
   z `/edycje` (jest na rozmaitości), potem ręcznie nadpisz rdzeń. Czy bije
   i dzikiego, i czysty wariant z dekodera? **To najwyżej rokujący nieprzetestowany
   kierunek.**
3. **Czy `N` może pomóc?** Do 10 % dozwolone, wchodzi jako 0,25 w każdym kanale.
   Czy `N` w pozycjach o zerowym gradiencie jest neutralne, czy szkodzi?
   Nietestowane, tanie do sprawdzenia.
4. **Czy naturalne promotory z `promotory_100.csv` biją dzikiego?** 100 sekwencji
   z 19 gatunków *Trichoderma*. Jeśli któreś wygrywa — mamy drugi punkt startowy
   i materiał na chimery.
5. **Czy Sędzia jest przechodni i powtarzalny?** Jeśli A>B i B>C, to czy A>C?
   Czy ten sam pojedynek daje ten sam wynik? Od tego zależy sensowność turnieju.
6. **Gdzie dokładnie leży próg czułości Sędziego** dla zmian *w latencie*
   (nie losowych)? Miareczkowanie 4.4 dotyczyło tylko losowych podstawień.
7. **Czy iterowana wspinaczka po kodach działa?** Podmień kod → dekoduj →
   pojedynek → przyjmij jeśli wygrał → powtórz z nowej bazy. Nietestowane.
8. **Jak wygląda `wagaP` dla wariantu, który wygrał?** Czy zwycięzcy mają
   inny rozkład gradientu niż przegrani? Potencjalnie tania funkcja zastępcza.
9. **[PRIORYTET] Czy edycje gatunkowe pomagają Wyroczni, mimo przegranej
   u Sędziego?** Patrz 4.2. Test: pula złożona z wariantów gatunkowo dopasowanych
   (rekomendacje `zmien_na` nanoszone pojedynczo i w kombinacjach), wgrana mimo
   negatywnego werdyktu Sędziego. Jeśli ranking wzrośnie — cała dotychczasowa
   selekcja była filtrowana złym kryterium.
10. **Czy `zmien_na` zmienia się dla sekwencji już zmodyfikowanych?** Nawigator
   liczy rekomendacje dla podanej sekwencji. Iteracja „nanieś → poproś o nowe
   rekomendacje → nanieś" może zbiegać do sekwencji maksymalnie dopasowanej do P1.
   Nietestowane, tanie.
11. **Czy Nawigator udostępnia sygnał siły niezależny od Sędziego?** `wagaP`
   pochodzi z głowicy promotorowej. Jeśli da się porównywać dwie sekwencje po
   rozkładzie `wagaP` (uwaga: legenda mówi wprost, że jest **nieporównywalna
   między sekwencjami** — więc trzeba znaleźć niezmiennik, np. udział masy
   gradientu w oknie rdzenia), mamy drugie proxy, niezależne od Sędziego.

---

## 8. Dostępne narzędzia (repo)

Repozytorium: klient Pythona bez zależności zewnętrznych, CLI, rejestr strategii,
65 testów offline. Kluczowe API biblioteki:

```python
from hyppe import Client, fasta as F, seq as S
c = Client.from_env()

c.dziki_seq()                      # promotor wyjściowy, 800 pz
c.mapa(seq, od=0, ile=800)         # pełna mapa pozycji
c.edycje(seq, poziom, ile_kodow, opcji, ziarno)
c.lepsza(a, b)                     # bool: czy b bije a
c.turniej(baza, {etykieta: seq})   # [(etykieta, seq)] zwycięzców
c.ranking_swiss(kandydaci, rund)   # ranking bez każdy-z-każdym
c.wgraj(tekst_fasta)

F.waliduj(rekordy)                 # odtwarza filtry serwera lokalnie
S.mutuj / S.krzyzuj / S.wstaw / S.znajdz_iupac / S.gc
```

Nowa strategia = plik w `hyppe/strategie/` z dekoratorem `@strategia("nazwa")`,
zwracający `{etykieta: sekwencja}`. Katalog jest auto-importowany.

### Limity [Z DOKUMENTACJI]

Sędzia 600/min, Nawigator `/mapa` i `/edycje` po 600/min każdy, pozostałe POST
240/min, **wgranie raz na 5 minut**, plik do 2 000 000 znaków.
`/me`, `/ranking`, `/dziki` bez limitu. Klient sam pilnuje limitów i ponawia
503 oraz 429 (poza `/wgraj`, gdzie 429 znaczy „czekaj").

**Limity są wysokie i nie są wąskim gardłem.** Wąskim gardłem jest okno 5 minut
na zgłoszenie i brak atrybucji wyniku do pojedynczych sekwencji.

---

## 9. Wymagania wobec każdej propozycji

Każde proponowane rozwiązanie musi:

1. produkować sekwencje **dokładnie 800 pz** ze znaków `ACGTN`, ≤ 10 % `N`, unikalne;
2. dawać **100 sekwencji** — mniej to proporcjonalna strata w ALL100;
3. dać się zweryfikować przed wgraniem — przy czym **Sędzia służy wyłącznie jako
   bramka „czy to nadal promotor"**, a nie jako miara siły; przegrana u Sędziego
   **nie jest** wystarczającym powodem do odrzucenia wariantu (patrz 2.1 i 4.2);
4. mieć **uzasadnienie biologiczne**, nie tylko „model tak powiedział" —
   50 % oceny to prezentacja, gdzie liczą się metodyka, ogólność, ograniczenia
   i odpowiedzi na pytania Jury;
5. uwzględniać, że **losowe edycje w przestrzeni liter nie działają** (4.4, 4.5) —
   propozycja oparta na losowym mutowaniu DNA jest sprzeczna z pomiarami;
6. brać pod uwagę, że **Sędzia to proxy, które może się rozjeżdżać z Wyrocznią**.

Priorytet: **TOP10** (serwer po niej wybiera najlepsze zgłoszenie), przy
utrzymaniu wysokiej średniej ALL100. Praktycznie oznacza to portfel: większość
puli wokół sprawdzonej rodziny, mniejszość jako zróżnicowane zakłady na ogon.
Jedna słaba sekwencja kosztuje 1/100 średniej i **nie szkodzi TOP10 w ogóle**,
więc ryzykowne zakłady są tanie.
