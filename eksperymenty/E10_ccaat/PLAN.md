# E10 · CCAAT — pierwsza hipoteza z uzasadnieniem biologicznym

**Status:** wyliczone offline z `E03/wyniki.json`, **zero wywołań API** ·
**Zależy od:** v4 (100 niezależnych ziaren)

---

## Skąd to się wzięło

Po dziewięciu eksperymentach mieliśmy **zero wniosków biologicznych**. Wszystko,
co znaleźliśmy — artefakt brzegowy `wagaP`, `blad_odtworzenia` jako detektor
pochodzenia, wysycenie Sędziego, dominacja ziarna nad operatorem — dotyczy
**architektury narzędzi**, nie promotorów. To są wnioski o modelu, nie o *pks1*.

Jednocześnie leżał nietknięty jedyny zbiór w projekcie, który **nie pochodzi
z modelu**: sto naturalnych promotorów *Trichoderma* z dziewiętnastu szczepów.
E03 użyło go tylko do pytania „czy któryś bije dzikiego" (0/100) i do konsensusu
rdzenia — który zresztą unieważnił E02.

Ta analiza to porównanie dzikiego promotora `pks1` z tym zbiorem. Liczy się
lokalnie, w kilkanaście sekund, i nie zużywa ani jednego okna.

---

## Wynik 1 — rdzeń promotora istnieje i jest w ostatnich 50 pz

Informacja pozycyjna (2 − entropia kolumny) w stu promotorach wyrównanych do TSS:

```
okno         średnia IC (bity)
  1-700         0,019 – 0,030      tło
701-750         0,042              2,0 × tło
751-800         0,055              2,6 × tło

poz. 798 (TSS−2)   IC = 0,525   →  A w 62/100 promotorów   (25 × tło)
```

To jest **rdzeń promotora wyprowadzony z danych biologicznych**, a nie
z gradientu modelu. Zastępuje martwą historię o oknie 783–800 z `wagaP`
(E02: artefakt brzegowy) czymś, co da się obronić przed Jury: silna preferencja
puryny A dwie zasady przed końcem to podręcznikowy element **Inr**.

## Wynik 2 — ale rdzeń `pks1` jest **normalny**, więc nie tam jest problem

Log-odds wobec macierzy PWM zbudowanej ze stu naturalnych:

| okno | naturalne (mediana) | dziki `pks1` | percentyl |
|---|---|---|---|
| **rdzeń 751–800** | 2,97 | **3,67** | **52 %** |
| kontrola 401–450 | 1,35 | −0,33 | 25 % |

`pks1` ma **przeciętny, poprawny rdzeń**. Kontrola pokazuje, że PWM w ogóle coś
mierzy (w losowym oknie dziki wypada poniżej normy, w rdzeniu w normie).

> **To wycina blok „edycja rdzenia" z planu.** Nie ma czego naprawiać —
> dziki już ma rdzeń taki, jaki mają inne promotory *Trichoderma*.

## Wynik 3 — `pks1` nie ma **ani jednego** miejsca CCAAT

Skan obu nici (`CCAAT` + `ATTGG` — element działa niezależnie od orientacji):

| motyw | dziki | mediana naturalnych | % naturalnych z ≥ 1 |
|---|---|---|---|
| **CCAAT / ATTGG** | **0** | **2** | **81 %** |
| CreA `SYGGRG` | 2 | 2 | 92 % |
| Inr-podobny | 1 | 1 | 65 % |
| TATAAA | 1 (na −457) | 0 | 43 % |
| GC-box | 0 | 0 | 33 % |

**CCAAT to jedyny motyw, w którym dziki odstaje od normy.** Przy pozostałych
jest dokładnie na medianie.

### Mechanizm (literatura, nie nasze dane)

CCAAT wiąże **kompleks CBC / HAP** (HapB–HapC–HapE u *Aspergillus nidulans*,
homologi w całych grzybach strzępkowych, w tym *Trichoderma*). To czynnik
architektoniczny i aktywujący: zagina DNA, przesuwa nukleosom i otwiera region
dla maszynerii podstawowej. Jeden z najlepiej udokumentowanych ogólnych
aktywatorów transkrypcji u grzybów strzępkowych.

### Gdzie *Trichoderma* trzyma te miejsca

199 miejsc w stu promotorach, mediana pozycji **−388** od TSS, najgęstsze okna
50 pz: **−300…−251** (n = 19) i **−250…−201** (n = 21). Rozkład szeroki,
z wyraźnym zagęszczeniem w pasie −500…−200.

### Uczciwe zastrzeżenie — i to trzeba powiedzieć Jury pierwszemu

Brak CCAAT w `pks1` **nie jest anomalią statystyczną**. Z samego składu zasad
oczekujemy 1,62 trafienia, więc `P(0) = e^−1,62 = 0,20`. Zera ma też 19 ze stu
naturalnych promotorów. Wzbogacenie naturalnych ponad losowe tło to zaledwie
1,28 ×.

> Nie twierdzimy „`pks1` jest zubożony w CCAAT". Twierdzimy: **81 % promotorów
> *Trichoderma* niesie udokumentowany element aktywujący, którego `pks1` nie ma,
> a jego instalacja kosztuje jedno podstawienie.** Do decyzji inżynierskiej
> wystarczy mechanizm i cel — nie jest potrzebna istotność statystyczna anomalii.

---

## Projekt: cztery podstawienia, cztery miejsca CCAAT

Dziki jest **jedną zasadą** od pełnego CCAAT w 22 miejscach. Cztery z nich leżą
w pasie, w którym naturalne promotory zagęszczają te miejsca:

| poz. | TSS | jest | cel | podstawienie | gęstość u naturalnych |
|---|---|---|---|---|---|
| 546 | −254 | `CCAAC` | `CCAAT` | 550 C→T | 19 (najgęstsze okno) |
| 317 | −483 | `ATTGT` | `ATTGG` | 321 T→G | 17 |
| 391 | −409 | `CCACT` | `CCAAT` | 394 C→A | 13 |
| 355 | −445 | `CCAAC` | `CCAAT` | 359 C→T | 13 |

Efekt: **4 zmiany na 800 pz**, GC 47,5 % → 47,2 %, cztery funkcjonalne miejsca
CCAAT rozstawione tam, gdzie trzyma je organizm.

### Dlaczego to nie jest sprzeczne z W5 („losowe mutacje nie działają")

W5 obalił **losowe** podstawienia — 0/80, bo losowa zmiana zrzuca sekwencję
z rozmaitości modelu i nic nie wnosi. Tutaj każda zmiana **tworzy nazwany
element wiązania białka** w pozycji wyprowadzonej z danych. To jest różnica
między szumem a projektem, i dokładnie o nią pyta Jury.

Sędzia najprawdopodobniej tego nie zauważy albo ukarze — mierzy prototypowość
wyjścia dekodera (W4), a nie obecność miejsc wiązania. **To nie jest powód do
odrzucenia** (patrz W4, W7 i rewizja z 4.2 briefu).

---

## Realizacja: naszczepienie na 100 niezależnych ziaren

K1 jest wyczerpany (W24: 56 → 100 ziaren nie ruszyło TOP10; rozkład ma sufit).
CCAAT to **inny wymiar**, nie większa próba z tego samego rozkładu — więc
łączymy jedno z drugim:

```
v4.fasta  =  100 ziaren, każde z osobnego skupienia   (najlepsza znana baza)
v8.fasta  =  te same 100 ziaren + naszczepione CCAAT   (ta sama różnorodność,
                                                        nowy wymiar)
```

Zachowujemy 100 niezależnych korzeni **i** dokładamy oś, na którą narzędzia są
ślepe. Koszt: 0 wywołań na budowę, ~20 na kontrolną próbkę bramki.

```bash
python eksperymenty/E10_ccaat/run.py                    # analiza + v8.fasta
python -m hyppe waliduj runs/julian/v8_ccaat.fasta
python -m hyppe wgraj  runs/julian/v8_ccaat.fasta
```

## Co to daje na prezentacji

Do tej pory mieliśmy cztery wyniki negatywne o narzędziach i zero biologii.
To jest pierwszy slajd, na którym pada nazwa białka:

1. rdzeń promotora **znaleziony z konserwacji** w stu promotorach, nie z modelu —
   i pokazany obok artefaktu `wagaP`, który znaleźliśmy i odrzuciliśmy;
2. `pks1` ma rdzeń w normie → **nie ruszamy go** (wynik negatywny, który
   oszczędził 30 sekwencji);
3. `pks1` nie ma elementu, który ma 81 % rodzaju → **instalujemy go**,
   z mechanizmem (kompleks CBC/HAP) i z pozycją wziętą z rozkładu naturalnego;
4. i od razu ograniczenie: to nie jest anomalia statystyczna, to decyzja
   inżynierska. Powiedziane przez nas, zanim zapyta Jury.
