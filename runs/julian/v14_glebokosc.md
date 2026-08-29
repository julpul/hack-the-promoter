# v14_glebokosc.fasta

**Zbudowane:** 2026-08-29 · `eksperymenty/E13_glebokosc/run.py` · **status: niewgrane**

---

## Dlaczego akurat to

Po trzynastu zgłoszeniach obraz jest jednoznaczny: **przejście przez dekoder
to jedyna interwencja, która kiedykolwiek dała duży zysk.**

```
dziki + 1 podstawienie          5,0 pkt    TOP10 poz. 9
ziarna dekodera                14,0 pkt    TOP10 poz. 4
```

Pięć pozycji rankingu. Wszystko, co dokładaliśmy **na** ziarnach — CCAAT,
edycje gatunkowe, poli(dA:dT), tandemowy UAS, usunięcie CreA, usunięcie
elementów świetlnych — mieści się w paśmie **12–14 punktów**, czyli w szumie
wokół plateau. Sześć różnych dodatków, żaden nie ruszył wyniku.

Wniosek: przestajemy dokładać nowe osie i **pchamy tę jedną, która działa**.

## Czego już wiemy, że nie zadziała

**Dosłowne powtórzenie skoku nie działa** (E06/R6): drugie pokolenie bije
dzikiego w 11/16 przypadków, ale **nie bije własnego rodzica ani razu**
(0/16 w E06, 1 przypadek na 494 w E07). `blad_odtworzenia` spada z 80 do ~21
w jednym przejściu i kolejne przejścia go nie obniżają. To **jednorazowy skok
na rozmaitość**, nie proces iterowalny.

Ale to nie znaczy, że oś jest wyczerpana — znaczy, że pchaliśmy ją złą metodą.

---

## Co jest w pliku

| blok | n | co testuje |
|---|---|---|
| **A — głębokość** | 45 | ziarna z **najniższym `blad_odtworzenia`** z dużego przesiewu |
| **B — pokolenie** | 45 | drugie i trzecie przejście przez dekoder, dalej wzdłuż kierunku |
| **K — kontrola** | 10 | obecne ziarna z `v4.fasta` |

### Blok A — głębokość, której nigdy nie sortowaliśmy

Ziarna wybieraliśmy zawsze **bramką binarną** („bije dzikiego"), nigdy według
tego, jak głęboko leżą na rozmaitości modelu. Pomiar na naszych 100 ziarnach
pokazuje, że rozrzut jest realny:

```
blad_odtworzenia : 13 – 21 – 34   (min/mediana/maks, odch. 4,0)
```

Jeśli to, co daje punkty, to „jak dobrze model rozpoznaje sekwencję jako swoją",
to ziarna z 13–15 powinny bić te z 30–34. Przesiewamy ~1200 losowań i bierzemy
skrajny kwantyl zamiast pierwszych, które przeszły bramkę.

### Blok B — dalej wzdłuż tego samego kierunku

Nasze ziarna leżą **102–133 pz** od dzikiego. Zestaw wyników układa się
monotonicznie wzdłuż dystansu — **w obrębie rodziny pochodnej dekodera**:

```
dystans     1  →   5,0 pkt   (B0, linia bazowa)
dystans    64  →   8,0 pkt   (B1, poli-dA:dT)
dystans   115  →  14,0 pkt   (ziarna)
dystans  300+  →   4,0 pkt   (chimery — ale to INNY kierunek, obce DNA)
```

Czego jest na 150–250 wzdłuż kierunku dekodera — nie wiemy. Drugie i trzecie
pokolenie leżą właśnie tam. Każde kolejne pokolenie musi przejść bramkę, żeby
wejść do puli, więc nie zbieramy sekwencji zepsutych.

### Blok K — po co kontrola

Bez niej wynik będzie nieodczytywalny. Jeśli A i B nie przebiją K, znaczy to,
że ani głębokość, ani dystans nie mają znaczenia — a nie że „nic nie działa".
Dziesięć sekwencji wystarczy, bo TOP10 bierze dziesięć najlepszych: jeśli
kontrola jest najlepsza, zdominuje dziesiątkę mimo małej liczebności.

---

## Zastrzeżenie metodyczne, które trzeba wypowiedzieć

W18 pokazał, że `blad_odtworzenia` **nie przewiduje werdyktu Sędziego**
wewnątrz jednorodnej puli (d Cohena = +0,06). Można by z tego wnioskować,
że blok A nie ma sensu.

**To byłby ten sam błąd, który popełniliśmy przy edycjach gatunkowych.**
Sędzia jest **wysycony** — nie szereguje niczego powyżej progu „to jest
promotor" (W4, W6: plateau po jednym kroku wspinaczki). Brak korelacji
z Sędzią **nie jest dowodem** co do Wyroczni, bo Sędzia z definicji nie
rozróżnia w tym zakresie. Jedynym instrumentem, który to rozstrzygnie,
jest wgranie.

---

## Jak odczytać wynik

| wynik | wniosek |
|---|---|
| A > K | głębokość na rozmaitości ma znaczenie → przesiewać agresywniej i sortować |
| B > K | dystans wzdłuż kierunku dekodera ma znaczenie → iść w dalsze pokolenia |
| A ≈ B ≈ K | oś dekodera **wyczerpana** — zysk jest jednorazowy i skończony |
| A < K lub B < K | jesteśmy już za daleko; optimum leży bliżej dzikiego niż sądziliśmy |

Ostatni wiersz jest równie wartościowy jak pierwsze dwa: powiedziałby, że
plateau 12–14 to nie sufit narzędzia, tylko **optimum**, które przypadkiem
trafiliśmy pierwszym przesiewem.

---

## Wynik po wgraniu

Wgrane **2026-08-29 18:52** czasu lokalnego (16:52:28 czasu serwera).

| pole | przed (v8_ccaat) | po v14 | zmiana |
|---|---|---|---|
| TOP10 | 7,0 (ranga 4) | **8,0 (ranga 3)** | +1 ranga |
| ALL100 | 5,0 (ranga 6) | **6,0 (ranga 5)** | +1 ranga |
| razem | 12,0 | **14,0** | **+2,0** |

**Pierwsze zgłoszenie od 14:41, które pobiło nasze własne.** I to na obu
polach naraz — a ALL100 był naszym najsłabszym.

### Co ten wynik naprawdę mówi

Sześć poprzednich zgłoszeń trafiało w pasmo 12–14 i wyglądało to na sufit
metody. Nie było sufitem. Ziarna wybieraliśmy **bramką binarną** („bije
dzikiego") i nigdy ich nie szeregowaliśmy. Ten sam mechanizm losowania,
**posortowany po `blad_odtworzenia`**, dał +2,0 punktu.

Liczby z przebiegu (1600 losowań, 74 s w 16 wątkach):

```
przez bramkę        138 / 1600   (8,6 %)
blad_odtworzenia    9 – 21 – 39   (min/mediana/maks w całej puli)
wybrane (blok A)    9 – 19        (45 najgłębszych)
blok B, dystans     123 – 142 – 171   (poprzednie ziarna: 102–133)
```

Kluczowe: **9** to głębiej niż minimum naszych stu dotychczasowych ziaren
(13). Poprzednio braliśmy pierwsze, które przeszły bramkę — czyli losową
próbkę z pasma 13–34. Teraz bierzemy ogon rozkładu.

### Czego ten wynik NIE mówi

Plik miesza trzy bloki (A = głębokość 45, B = pokolenia 45, K = kontrola 10),
więc **nie wiemy, który blok dał zysk.** Możliwe, że cały +2,0 pochodzi
z bloku A, a blok B jest neutralny — albo odwrotnie. Rozdzielenie tego jest
przedmiotem E14 (`eksperymenty/E14_kompozycja/PLAN.md`, sekcja o atrybucji).

Metodycznie ważne: W18 („`blad_odtworzenia` nie przewiduje werdyktu Sędziego",
d = +0,06) **nie został obalony** — został potwierdzony jako nieistotny.
Sędzia jest wysycony i nie szereguje; głębokość szereguje. To dwie różne
rzeczy i dobrze, że nie posłuchaliśmy Sędziego.
