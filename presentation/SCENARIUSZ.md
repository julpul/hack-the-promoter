# Prezentacja — tekst do przeczytania

**4 minuty · 5 slajdów · drużyna 01**

Pod każdym slajdem jest tekst do powiedzenia na głos. Na slajd idzie tylko
nagłówek, punkty i diagram — reszta to mowa.

**Diagramy** (w `presentation/wykresy/`), po jednym na slajd 2, 4 i 5:

| slajd | plik | co pokazuje |
|---|---|---|
| 2 | `s2_narzedzia.png` | dwie liczby: `0 z 180` i `100 ze 101` |
| 4 | `s4_przelom.png` | trzy słupki: 4 · 5 (linia zero) · 14 |
| 5 | `s5_dryf.png` | ten sam plik: 14 o 18:52, 12 o 19:55 |

Slajdy 1 i 3 są bez diagramu — tytułowy i lista odrzuconych pomysłów bronią
się samym tekstem, a cztery obrazki na cztery minuty to i tak dużo.

---

## SLAJD 1

# Jak ulepszaliśmy gen, nie widząc, co właściwie poprawiamy

**Promotor `pks1` z grzyba *Trichoderma* · 800 liter DNA**

---

**Do powiedzenia:**

Dostaliśmy jeden gen — promotor `pks1`, osiemset liter DNA. Zadanie: zrobić
z niego mocniejszy. Do tego trzy narzędzia i ranking, w którym widać tylko
nasze miejsce, nigdy ocenę.

Opowiem, jak myśleliśmy. Razem z tym, gdzie się pomyliliśmy — bo to była
większość drogi i to jest najciekawsza część.

---

## SLAJD 2

# Najpierw sprawdziliśmy, czy narzędzia mówią prawdę

- **Sędzia** — porównuje dwie sekwencje, mówi która lepsza
- **Mapa modelu** — pokazuje, na co model patrzy
- Oba okazały się mierzyć **coś innego**, niż obiecywały

---

**Do powiedzenia:**

Pierwszy odruch to od razu zacząć projektować. Nie zrobiliśmy tego. Najpierw
sprawdziliśmy, czy narzędzia w ogóle mierzą to, co obiecują.

Sędzia miał mówić, która sekwencja jest silniejsza. Daliśmy mu sto prawdziwych
promotorów z natury — żaden nie wygrał z naszym. Potem osiemdziesiąt losowych —
też żaden. Więc Sędzia nie ocenia siły. On tylko rozpoznaje, czy coś w ogóle
wygląda jak promotor.

Drugie narzędzie pokazywało, gdzie model patrzy. Zawsze wskazywało koniec
sekwencji. Sprawdziliśmy to: obróciliśmy sekwencję, pomieszaliśmy litery,
wstawiliśmy czysty bełkot. Wskazanie ani drgnęło — sto razy na sto jeden ten
sam punkt. To nie była biologia. To był artefakt.

Wniosek był niewygodny: **nie mamy miernika jakości.** Jedyny prawdziwy pomiar
to wysłać zgłoszenie i zobaczyć, czy ruszyliśmy się w rankingu.

---

## SLAJD 3

# Cztery pomysły, które sprawdziliśmy i odrzuciliśmy

- Edytować tam, gdzie patrzy model → **artefakt**
- Dużo losowych mutacji → **0 wygranych na 80 prób**
- Mieszać z prawdziwymi promotorami → **gorzej niż nic nie robić**
- Więcej prób, z 3 na 100 → **wynik nie drgnął**

---

**Do powiedzenia:**

Więc zaczęliśmy zgadywać — ale po kolei i zawsze z kontrolą.

Pomysł pierwszy: skoro model patrzy na koniec, edytujmy koniec. Odpadł, bo to
był właśnie ten artefakt.

Drugi: może wystarczy dużo losowych mutacji. Osiemdziesiąt prób, do sześciuset
zmienionych liter. Ani jednej wygranej.

Trzeci: weźmy prawdziwe promotory z natury i pomieszajmy je z naszym. To
wypadło **gorzej**, niż gdybyśmy zmienili w oryginale jedną literę. Obce DNA
po prostu szkodzi.

Czwarty: może potrzebujemy więcej prób. Zwiększyliśmy z trzech niezależnych
startów do stu. Wynik nie drgnął ani o krok.

To brzmi jak seria porażek, ale każda z nich odcinała kawałek przestrzeni.
I wynikła z nich jedna rzecz, która okazała się kluczowa.

---

## SLAJD 4

# Przełom: brakowało nam punktu zerowego

- Wysłaliśmy oryginał ze **zmienioną jedną literą** — to nasza linia zero
- Okazało się, że stoimy **pięć miejsc wyżej**, tylko nie było z czym porównać
- Zysk dawało jedno przepuszczenie sekwencji przez model
- Potem: **posortowanie** wyników zamiast brania pierwszego lepszego → **awans o dwa miejsca**

---

**Do powiedzenia:**

Zrobiliśmy najprostszą możliwą rzecz. Wysłaliśmy oryginał ze zmienioną jedną
literą. To była nasza linia zero. I dopiero wtedy zobaczyliśmy, że nasze
zgłoszenia stoją pięć miejsc wyżej. Przez pół dnia wydawało nam się, że nic
nie działa — a działało. Po prostu nie mieliśmy z czym porównać.

Co dawało ten zysk? Jedno przepuszczenie sekwencji przez model. On przepisuje
ją po swojemu, zmieniając około stu liter. To odpowiadało za jakieś
dziewięćdziesiąt procent całej poprawy.

I znaleźliśmy jeszcze jedno. Te przepisane wersje wybieraliśmy metodą
„przeszła albo nie przeszła". Nigdy nie ustawialiśmy ich w kolejności. Kiedy
posortowaliśmy je według tego, jak dobrze model rozpoznaje je jako swoje,
i wzięliśmy najlepsze — awansowaliśmy o dwa miejsca. Pierwsza poprawa od
czterech godzin.

---

## SLAJD 5

# Najważniejsze, czego się nauczyliśmy

- Zbudowaliśmy **cztery warianty**, żeby sprawdzić, co dokładnie zadziałało
- Wszystkie cztery wypadły **gorzej**
- Więc wysłaliśmy **ten sam plik jeszcze raz** — i dostał **mniej punktów**
- Ranking punktuje **miejsce**, nie wartość. Pole przesuwa się pod nami

---

**Do powiedzenia:**

I tu przychodzi wynik, który zmienił nam obraz wszystkiego.

Chcieliśmy sprawdzić, co dokładnie zadziałało, więc zbudowaliśmy cztery
warianty — każdy testował jedno wyjaśnienie. Wszystkie cztery wypadły gorzej
niż nasz najlepszy plik.

Więc zrobiliśmy kontrolę. Wysłaliśmy jeszcze raz dokładnie ten sam plik, który
godzinę wcześniej dał nam najlepszy wynik. Dostał **mniej**.

Ten sam plik. Te same sekwencje. Niższy wynik. Bo ranking punktuje miejsce,
a nie wartość — inne drużyny wysyłały w międzyczasie i pole przesunęło się pod
nami. Czyli nasze cztery „gorsze" warianty wcale nie były gorsze. Przez godzinę
optymalizowaliśmy szum i nie mieliśmy o tym pojęcia.

To jest najważniejsza rzecz, jaką dziś zmierzyliśmy. W takim rankingu **bez
powtórzenia pomiaru można gonić własny ogon i tego nie zauważyć.**

Dlatego ostatnią rzeczą, jaką zrobiliśmy, było wrócenie do biologii —
do elementów, o których wiadomo z literatury, że działają, i które nasz gen
ma w liczbie zero. To jedyna część tego projektu, w której coś naprawdę
zaprojektowaliśmy, zamiast losować.

---

# Notatki

**Czas:** 547 słów mówionych — **3:54** w normalnym tempie, 4:23 jeśli mówisz
wolno. Czyli mieścisz się z zapasem na jedno potknięcie.
Jeśli mimo to trzeba skrócić — najłatwiej wyciąć czwarty pomysł ze slajdu 3
(„więcej prób") i ostatni akapit slajdu 5.

**Gdyby padło pytanie „to ile ostatecznie zyskaliście":**
oryginał ze zmianą jednej litery to 5 punktów, nasz najlepszy plik to 14 —
przy czym ten sam plik godzinę później dawał już 12, i właśnie o tym jest
slajd piąty.

**Gdyby padło pytanie „co byście zrobili dalej":**
powtórzenia zamiast nowych pomysłów. Każdy wariant wysłaliśmy raz, a przy
ruchomym rankingu jeden pomiar nie wystarcza, żeby cokolwiek twierdzić.
