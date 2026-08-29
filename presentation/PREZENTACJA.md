# Prezentacja — content do wklejenia

**Drużyna 01 · Hack the Promoter · 2026-08-29 · 5 slajdów / 4 min**

Wykresy leżą w `presentation/wykresy/` jako PNG:
`1_historia.png` · `2_rodziny.png` · `3_zrodlo.png` · `4_cis.png`

Poniżej: treść slajdu (nagłówek + punkty) i pod nią **notatka prelegenta**
z chronometrażem. Notatek się nie wkleja na slajd.

---

## SLAJD 1 — tytuł · 20 s

# Ślepy sędzia, ślepa mapa, ślepy gradient
### Jak optymalizować promotor, gdy żaden przyrząd nie mierzy celu

**Drużyna 01** · `pks1` z *Trichoderma* · 800 pz
14 eksperymentów · 24 zgłoszenia · linia bazowa 5,0 → nasz wynik 14,0

> **Notatka (20 s):** Nie zaczynaliśmy od projektowania sekwencji. Zaczęliśmy
> od zmierzenia, co właściwie mierzą narzędzia, które dostaliśmy. To zajęło
> pierwsze pięć eksperymentów i okazało się najlepszą inwestycją dnia.

---

## SLAJD 2 — czego użyliśmy i co te narzędzia naprawdę mierzą · 55 s

**Stos:** Python 3, klient API na samej bibliotece standardowej
(`hyppe/`, 4 endpointy), 14 eksperymentów w `eksperymenty/E01–E14`,
analiza w pandas/matplotlib.

**Trzy przyrządy — i wynik ich kalibracji:**

| przyrząd | co miał mierzyć | co mierzy naprawdę |
|---|---|---|
| **Sędzia** (`/sedzia`) | która sekwencja silniejsza | **wysycony** — 0/100 naturalnych promotorów i 0/80 losowych bije dzikiego; plateau po 1 kroku wspinaczki |
| **`wagaP`** (`/nawigator/mapa`) | gdzie model patrzy | **artefakt brzegowy** — szczyt na poz. 788 dla **100 ze 101** sekwencji, także dla rotacji, permutacji i poli-A |
| **`blad_odtworzenia`** | jakość sekwencji | **detektor pochodzenia** — dekoder 9–39, prawdziwe DNA 63–95, rozkłady rozłączne |

**Konsekwencja:** nie mamy funkcji celu. Jedyny pomiar jakości to wgranie
i odczyt rangi. Wszystko dalej jest projektowaniem eksperymentu wokół tego
ograniczenia.

> **Notatka (55 s):** Najważniejszy slajd. Podkreślić, że `wagaP` to pułapka
> — naturalne odruchowe „edytujmy tam, gdzie model patrzy" prowadzi w ślepy
> zaułek, i sami się na to nabraliśmy, zanim zrobiliśmy kontrolę z rotacją
> sekwencji. Jeśli ktoś z sali zapyta „czemu nie gradient" — bo gradient
> wskazuje krawędź wejścia splotu, nie biologię.

---

## SLAJD 3 — co zadziałało · 70 s

**Wykres:** `1_historia.png` (duży, lewa strona) + `3_zrodlo.png` (mały, prawa)

**Trzy rzeczy, które dały punkty:**

1. **Linia bazowa.** Dziki + 1 podstawienie = **5,0 pkt**. Bez tego punktu
   odniesienia przez pół dnia wyglądało, że „nic nie działa" — a nasze
   portfele stały na 12–14, czyli pięć rang wyżej.
2. **Ziarno dekodera** — jedno przejście przez `/nawigator/edycje` odpowiada
   za ~90 % całego zysku (5,0 → 14,0).
3. **Szeregowanie zamiast bramki.** Ziarna wybieraliśmy binarnie („bije
   dzikiego"). Posortowane po `blad_odtworzenia` dały **+2,0 pkt** — pierwsza
   poprawa od czterech godzin.

**Strojenie źródła (prawy wykres):** `poziom=2` z `ile_kodow` 48–64
przepuszcza przez bramkę **16 %** kandydatów wobec **3,5 %** dla
`poziom=1, ile_kodow=8`. Pięciokrotnie wydajniejsze losowanie —
tego nie mierzył nikt, bo wszyscy patrzyli na dystans, nie na przelotowość.

> **Notatka (70 s):** Historia „nic nie działa → działa, tylko nie było
> z czym porównać" jest tu najmocniejsza. Linia bazowa to nie formalność,
> to była nasza największa pojedyncza wygrana poznawcza.

---

## SLAJD 4 — gdzie się zatrzymaliśmy i dlaczego · 70 s

**Wykres:** `2_rodziny.png` (na cały slajd)

**Cztery hipotezy, cztery falsyfikacje — w ciągu jednej godziny:**

| hipoteza | test | wynik |
|---|---|---|
| głębiej na rozmaitości = lepiej | v15: 100 × najgłębsze | 12,0 |
| dalej wzdłuż osi dekodera = lepiej | v16: dystans 192–262 | 11,0 |
| więcej rodzin w portfelu = lepiej | w18: 5 rodzin × 20 | 12,0 |
| koniunkcja: głęboko **i** w pasie 120–180 | v22: `blad` 0–2–4, dyst. 123–176 | 12,0 |

**I pomiar, który to wszystko przewartościował:**
ten sam plik `v14`, wgrany o **18:52 dał 14,0**, a o **19:55 dał 12,0**.

Ranking punktuje **rangę**, nie wartość. Pole rusza się pod nami — nasza
pozycja spadła z 5. na 7. przy **niezmienionym zgłoszeniu**. Czyli różnica
12 vs 14 nie była sygnałem z naszych sekwencji. **Przez godzinę
optymalizowaliśmy szum.**

**Jedyna twarda granica, jaką znaleźliśmy:** powyżej ~**180 pz** od dzikiego
wynik się załamuje (v16 = 11,0; chimery z obcego promotora na 300+ pz = 4,0,
poniżej linii bazowej).

> **Notatka (70 s):** To jest slajd, który zjedna jury, jeśli powiedzieć go
> wprost: mieliśmy hipotezę, zbudowaliśmy pod nią test, test ją obalił,
> i powtórzyliśmy to cztery razy. A na końcu kontrola pokazała, że sam
> przyrząd pomiarowy dryfuje. Nie chować tego — to jest wynik.

---

## SLAJD 5 — projekt zamiast losowania · 55 s

**Wykres:** `4_cis.png`

**Jedyna część projektu, w której coś zaprojektowaliśmy** — `strategie.py`,
bloki o znanej funkcji, każdy z nazwą białka i cytowaniem:

| blok | białko | uzasadnienie w naszych danych |
|---|---|---|
| **CCAAT ×4** | Hap2/3/5 (CBC) | dziki ma **0**, mediana 100 naturalnych = 2, **percentyl 0 %** |
| **IR-XBS** | Xyr1 / ACE2 | dziki ma **0** miejsc `GGCTAA`; układ odwrócony powtórzony — element **inżynierski**, nie ma go żaden ze 100 naturalnych |
| **poli(dA:dT)** | architektura nukleosomowa | `AOX1` u *P. pastoris*: 0,25–3,5 × dzikiego |
| **Cre1 rozbite** | represja kataboliczna | metoda z `cbh1`: wymiana miejsc represora na aktywatory → 5,0 × i 3,6 × |

**Co byśmy zrobili z kolejną godziną:**
1. **Replikacja przepisu v14** z innymi ziarnami — jedyny test, który rozdziela
   „sygnał" od „szczęśliwego losowania". Nie zdążyliśmy.
2. **Powtórzenia zamiast nowych osi** — przy rankingu rangowym jeden pomiar
   na wariant to za mało, żeby cokolwiek twierdzić.
3. Domknąć pas **poniżej 120 pz** — cały ten zakres mamy pokryty jedną
   sekwencją (linia bazowa).

> **Notatka (55 s):** Zakończyć na tym, że biologia bloków jest gotowa
> i przetestowana offline (podkład miał CCAAT=0 → po złożeniu 4), ale
> zabrakło okien wgrania, żeby ją zmierzyć. Uczciwie: mamy projekt,
> nie mamy jeszcze na niego dowodu.

---

# Ściągawka liczbowa

Gdyby padło pytanie z sali.

| liczba | znaczenie |
|---|---|
| **5,0** | linia bazowa: dziki + 1 podstawienie |
| **14,0** | nasz najlepszy odczyt (v14, 18:52) |
| **12,0** | ten sam plik o 19:55 — miara dryfu pola |
| **4,0** | chimery z obcego promotora — **poniżej** linii bazowej |
| **~180 pz** | ściana dystansu od dzikiego |
| **9,4 %** | przelotowość przez bramkę Sędziego (603 / 6432) |
| **3,5 % → 16,2 %** | zysk ze strojenia `poziom` / `ile_kodow` |
| **0 / 100 / 0 / 80** | naturalnych i losowych sekwencji, które pobiły dzikiego u Sędziego |
| **100 / 101** | sekwencji ze szczytem `wagaP` na poz. 788 niezależnie od treści |
| **74 s** | czas przesiewu po odkręceniu limitów (było ~12 min) |

# Co gdzie leży w repo

```
hyppe/                       klient API (tylko biblioteka standardowa)
  client.py                  limity, ponawianie, rownolegle()
eksperymenty/E01..E14/       po jednym katalogu na pytanie
  E14_kompozycja/
    PLAN.md                  co z pivota zostaje, a co upadlo
    strategie.py             bloki cis jako skladalne funkcje
    WNIOSKI.md               dokument decyzyjny
runs/julian/                 wszystkie zgloszenia + .md do kazdego
presentation/                ten plik + wykresy/
```
