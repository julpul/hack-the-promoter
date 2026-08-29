# PODSUMOWANIE — stan po ośmiu eksperymentach

**iGEM Warsaw 2026 · drużyna_01 · 2026-08-29**

Dokument scala `WNIOSKI.md` (rejestr chronologiczny, 23 wnioski) w jeden obraz:
**co wiemy, czego nie wiemy, i co z tego wynika dla następnego zgłoszenia**.

---

## 1. Jedno zdanie

Optymalizacja tego zadania **nie jest projektowaniem sekwencji, tylko loterią
rozstrzyganą przy losowaniu ziarna** — a jedyne, na co mamy wpływ, to **liczba
niezależnych losów w puli**.

---

## 2. Co zostało zmierzone

### 2.1 Narzędzia — czego naprawdę dostarczają

| narzędzie | co miało robić | co robi naprawdę | dowód |
|---|---|---|---|
| **Sędzia** | mierzyć siłę promotora | binarna bramka „czy to prototypowy promotor"; wysycony powyżej progu | W4, W5, W6, W12 |
| **`wagaP`** | mapa ważności pozycji | **artefakt brzegowy** — szczyt na poz. 788 dla 100/101 sekwencji | W10 (E02) |
| **`zmien_na`** | dopasowanie do szczepu P1 | działa na własnej osi, ale nie wyróżnia P1 | W14, W19 |
| **`blad_odtworzenia`** | kandydat na funkcję celu | **detektor pochodzenia**, nie miara jakości | W13, W17 |
| **`/edycje`** | sterowana eksploracja | generator losowy; `ile_kodow` prawie bez wpływu | W2, W21 |
| **Wyrocznia** | ocena | niedostępna; 2 liczby na 5 minut | — |

**Nie mamy funkcji celu.** Wszystkie cztery skalary z nagłówka `/mapa` wariują
i są deterministyczne, ale żaden nie przewiduje werdyktu Sędziego wewnątrz
jednorodnej próby (|d| ≤ 0,26 — W18). Selekcja może się opierać wyłącznie
na binarnej bramce.

### 2.2 Mechanizm, który faktycznie działa

Łańcuch trzech kontroli (E06 → E07 → E08):

1. **To nie operator.** Krzyżowanie dwóch przegranych: **0/16**. Krzyżowanie
   dwóch zwycięzców: 9/16. Zwykła mutacja zwycięzcy o ten sam dystans: 8/16.
   Operator nie robi nic — liczy się, **od kogo zaczynasz** (W20).
2. **To nie parametry.** Przy zbalansowanym `n = 96` odsetek trafień leży płasko
   5–11 % dla `ile_kodow` ∈ {8…32}. Monotoniczny trend z pierwszego przesiewu
   był artefaktem doboru próby (W21).
3. **To ziarno.** 784 losowania → 65 trafień → **65 osobnych skupień**,
   wzajemnie oddalonych o ≥ 44 pz (mediana 67). Żadna para nie jest tą samą
   rodziną. Chmura wokół ziarna dziedziczy ~58 % skuteczności, ale **nic nigdy
   nie przewyższa własnego rodzica: 1 przypadek na 494** (W20.3).

### 2.3 Dlaczego to przekłada się wprost na punkty

`TOP10` to **statystyka pozycyjna** — bierze dziesięć najlepszych ze stu.
Nagradza więc **efektywną liczbę niezależnych prób**, a nie średnią jakość.
Sto skorelowanych wariantów jednego ziarna to dla TOP10 **jedno losowanie**.

| zgłoszenie | skład | przechodzi bramkę | niezależnych korzeni | TOP10 | ALL100 |
|---|---|---|---|---|---|
| **v1** `pula.fasta` | `hybryda` | 39/100 | **3** | poz. 2 / 5 startujących | poz. 1 |
| **v3** `v3.fasta` | przesiew E07 | **100/100** | **56** | **poz. 4 / 10** | poz. 5 |

Porównanie pozycji jest mylące, bo między wgraniami liczba startujących wzrosła
z 5 do 10, a punktacja jest rangowa. Rozstrzyga co innego: **serwer trzyma
najlepsze zgłoszenie drużyny wybierane po TOP10**, a w rankingu widnieje
znacznik czasu v3. Czyli **v3 pobiło v1 w TOP10** — kierunek jest potwierdzony.

---

## 3. Czego nie wiemy — uczciwa lista

| pytanie | status | dlaczego to boli |
|---|---|---|
| Czy bramka Sędziego koreluje z Wyrocznią? | **nieznane** | jedyna przesłanka: v1 z 39 % przejść dostało ALL100 #1, v3 ze 100 % poprawiło TOP10. Dwa punkty danych. |
| Czy dopasowanie gatunkowe (A) pomaga? | **brak dowodu** | Sędzia nie widzi gatunku (W4), więc bramka nie może tego rozstrzygnąć |
| Czy usunięcie CreA (B) pomaga? | **brak dowodu** | efekt 0 we wszystkich metrykach Nawigatora (W19) — narzędzie jest ślepe na ten wymiar |
| Czy prototypowość szkodzi w ocenie Wyroczni? | **nieznane** | nasze sekwencje mają `blad_odtworzenia` ≈ 21 przy naturalnych 63–95 (W13) |
| Ile ziaren wystarczy do TOP10 #1? | **nieznane** | wiemy tylko, że 3 → poz. 2/5, a 56 → poz. 4/10 |

**Największe ryzyko metodyczne:** maksymalizujemy jedyne dostępne proxy, które
z definicji mierzy co innego niż cel. To podręcznikowe prawo Goodharta.
Jedyne zabezpieczenie, jakie mamy, to **różnorodność puli** i gotowość do
odczytania sygnału z rankingu zamiast z Sędziego.

---

## 4. Kierunki — co robić dalej

### K1 · Więcej niezależnych ziaren — **WYCZERPANY** *(E08, zmierzone)*

> **Wynik jest negatywny i unieważnia pierwotne oczekiwanie tej sekcji.**

E08 dobrało pulę do **110 ziaren** (594 losowania, 8,6 % trafień — zgodnie
z W21; tylko 6 odrzuconych jako to samo skupienie). `v4.fasta` = **100 ziaren,
każde z osobnego skupienia**: wzajemne dystanse 41–115 pz (mediana 70),
**0 z 4950 par** poniżej progu 40, próbka 25/25 przechodzi bramkę.

| zgłoszenie | niezależnych korzeni | TOP10 | ALL100 | punkty |
|---|---|---|---|---|
| v3 | 56 | poz. **4** | poz. 5 | 13,0 |
| **v4** | **100** | poz. **4** | poz. **4** | **14,0** |

**Podwojenie liczby niezależnych losowań nie ruszyło TOP10 ani o jedną
pozycję.** ALL100 wzrosło o jedną, co daje +1 punkt i awans na 4. miejsce
w klasyfikacji łącznej — ale mechanizm, który miał działać, nie zadziałał.

Interpretacja: TOP10 zależy od **górnego ogona rozkładu**, z którego losujemy,
a nie od liczby losowań. 56 i 100 prób z tego samego rozkładu dają niemal ten
sam maksymalny wynik. **Rozkład ziaren dekodera ma sufit i jesteśmy przy nim.**

> Konsekwencja dla planu: dalsze losowanie nie ma sensu. Potrzebujemy **innego
> rozkładu**, a nie większej próby z tego samego — czyli kierunków K3 i K5.

### K1b · Ziarno + edycja na osi rozłącznej *(nowy, nieprzetestowany)*

W12 ustalił, że pozycje hipotez są **rozłączne**: gatunek (154, 287, 362, 430,
434, 648, 750, 754, 778), CreA (560–565), rdzeń (783–800). Nic nie stoi na
przeszkodzie, żeby wziąć 100 ziaren z v4 — najlepszą znaną bazę — i nanieść
na każde edycje gatunkowe. Zachowujemy 100 niezależnych korzeni **i** dokładamy
wymiar, którego Sędzia nie widzi. Koszt: 100 wywołań `/mapa`.

### K1-oryginalny · Więcej niezależnych ziaren *(zrealizowany, patrz wyżej)*

Bezpośrednia konsekwencja W20–W22 i jedyny kierunek z **potwierdzonym
mechanizmem**. Cel: **100 ziaren, każde z osobnego skupienia** (v3 ma 56
korzeni na 100 sekwencji — 44 sloty marnują się na rodzeństwo).

Koszt: ~8 % trafień × 2 wywołania na losowanie ≈ 2 500 wywołań przy limicie
3 000/min. Kilka minut.

> Oczekiwany efekt: 56 → 100 niezależnych losów w TOP10, przy zerowym koszcie
> dla ALL100 (każde ziarno przechodzi bramkę).

### K2 · Zgłoszenie musi być dobre w OBU kategoriach naraz

Serwer wybiera najlepsze zgłoszenie **po TOP10**, ale punktuje wtedy **obie**
kategorie z tego samego pliku. Nie da się zachować ALL100 z v1 i TOP10 z v3 —
bierze się jeden plik. Dlatego portfel musi maksymalizować TOP10 **bez
poświęcania średniej**, a nie wybierać jedno z dwojga.

Praktycznie: wszystkie 100 sekwencji przechodzą bramkę (chroni średnią)
**i** pochodzą z różnych skupień (buduje ogon).

### K3 · Hedging biologiczny — osobnym zgłoszeniem, nie w tym samym pliku

Hipotezy A (gatunek) i B (CreA) nie mają dowodu, bo **narzędzia są na nie
ślepe** — to nie to samo co „są fałszywe". Wgrania są jednak darmowe
(liczy się najlepsze), a odstęp to 5 minut.

> Zamiast rozcieńczać portfel K1, wysyłamy **osobny plik** z blokiem
> gatunkowo-biologicznym i czytamy ranking. To jedyny sposób, żeby zdobyć
> dowód na wymiar, którego Sędzia nie mierzy — a przy okazji gotowy slajd.

### K4 · Test prawa Goodharta

Zbudować sekwencję celowo przesadzoną pod Sędziego (upchane TATA-boxy),
sprawdzić, że bramka ją kocha, i wysłać w puli. Jeśli ranking nie drgnie —
mamy **udokumentowany rozjazd proxy**, czyli najmocniejszy punkt prezentacji.
Koszt: jedno okno 5 minut.

### K5 · Naturalność jako regulator

`blad_odtworzenia` rozdziela zbiory rozłącznie (dekoder 16–27, naturalne 63–95).
Jeśli Wyrocznia była trenowana na prawdziwych promotorach, cała nasza pula
leży poza jej rozkładem treningowym. Test: pula z wartościami **w zakresie
naturalnym**, budowana przez ręczne edycje dzikiego zamiast przez dekoder.

Uwaga: to kłóci się z K1 (ziarna **są** wyjściami dekodera). Dlatego to również
**osobne zgłoszenie**, nie domieszka.

---

## 5. Kolejność działań

| # | krok | koszt | zależy od |
|---|---|---|---|
| 1 | E08: dobrać ziarna do 100 | ~5 min | — |
| 2 | Złożyć **v4** = 100 niezależnych ziaren, wgrać | okno 5 min | 1 |
| 3 | Odczytać ranking: czy TOP10 wzrósł względem v3 (poz. 4) | — | 2 |
| 4 | **v5** = blok gatunkowo-biologiczny (K3), wgrać | okno 5 min | — |
| 5 | **v6** = test Goodharta (K4) albo pula naturalna (K5) | okno 5 min | 3, 4 |

Wgrania nic nie ryzykują: **liczy się najlepszy wynik drużyny, nie ostatni**.
Jedyny koszt to okno 5 minut, a każde zgłoszenie jest **pomiarem**, którego
nie da się wykonać inaczej.

---

## 6. Co idzie na prezentację

Cztery rzeczy, z których **trzy są wynikami negatywnymi** — i to jest zaleta,
bo każda ma kontrolę, która ją unieważniła:

1. **E06** — kontrola, która obaliła nasz najlepszy wynik. Mieliśmy 72 % vs 6 %
   i gotową opowieść o sile rekombinacji; ramię „krzyżowanie przegranych"
   (0/16) pokazało, że operator nie robi nic.
2. **E07** — kontrola, która obaliła nasz własny trend. Ładna monotoniczność
   po `ile_kodow` okazała się artefaktem doboru próby przy niezbalansowanym *n*.
3. **W18** — konfundacja pochodzeniem: ten sam skalar ma d = −0,48 między
   grupami i +0,06 wewnątrz grupy.
4. **W15** — usterka narzędziowa produkująca `None` przez trzy eksperymenty.
   Liczby były prawdziwe, ale pochodziły ze skryptu obok pipeline'u.
   Odtwarzalność jest częścią wyniku.

Do tego **E02** jako przykład, że metryka udostępniona przez API (`wagaP`)
może być artefaktem architektury — i że rozstrzyga to jedna dobrze dobrana
kontrola (rotacja), a nie ilość danych.
