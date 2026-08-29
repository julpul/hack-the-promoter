# v13_uas_swiatlo.fasta

**Zbudowane:** 2026-08-29 · `eksperymenty/E12_uas_swiatlo/run.py` · **status: niewgrane**

---

## Skąd ten pomysł

Dwie przesłanki z literatury, których nie mieliśmy przy poprzednich zgłoszeniach.

**1. Architektura UAS.** W inżynierii promotorów grzybowych siłę stroi się
**tandemowymi powtórzeniami** elementu aktywującego (UAS) doklejonymi do rdzenia
promotora, a nie pojedynczymi miejscami rozrzuconymi po sekwencji. W *A. niger*
biblioteka syntetycznych promotorów powstała właśnie przez tandemowe składanie
UASa/UASb; w *T. reesei* 200-pz fragment z `Pcbh1` doklejony do `Pcdna1`
podniósł siłę promotora.

Nasz najlepszy plik `v8_ccaat` wstawiał CCAAT **rozproszone**. Architektury
tandemowej nikt nie sprawdził.

**2. Represja świetlna.** Opublikowano, że **światło hamuje biosyntezę 6PP**
u *T. atroviride* — najwyższa produkcja w ciemności, sygnał idzie przez kompleks
BLR (homolog White Collar). Skoro naszym zadaniem jest zwiększyć transkrypcję,
usunięcie elementów odpowiedzi na światło jest zdejmowaniem hamulca.

**Nasz pomiar to potwierdza jako anomalię:** dziki `pks1` ma **C-box GATCGA**
(kanoniczne miejsce wiązania WCC) na −523 oraz dwa powtórzenia GATN na −523
i −197. Mediana obu w stu naturalnych promotorach *Trichoderma* wynosi **0**.
Czyli ten promotor ma elementy świetlne **ponad normę rodzaju** — co jest
spójne z tym, że `pks1` to gen regulowany światłem.

---

## Co jest w pliku

Baza: **100 niezależnych ziaren dekodera z `v4.fasta`**. Bazy nie ruszamy —
W30 pokazał, że każde oddalenie od `pks1` pogarsza wynik (chimery = 4,0 pkt,
poniżej linii bazowej 5,0).

Cztery bloki po 25 sekwencji:

| blok | co testuje | interwencja |
|---|---|---|
| **A** | architektura tandemowa | blok UAS: 2–5 × CCAAT z przerywnikiem 5 pz, w jednym miejscu okna 294–612 |
| **B** | **KONTROLA WEWNĘTRZNA** | CCAAT rozproszone 1–4 sztuki (replikacja `v8`, naszego najlepszego) |
| **C** | tandem + zniesienie represji świetlnej | blok UAS + rozbite `GATCGA` i `GATNGATN` |
| **D** | tandem + zniesienie represji węglowej | blok UAS + rozbite wszystkie `SYGGRG` (CreA) |

Blok B jest po to, żeby wynik dało się odczytać. Jeśli A/C/D nie przebiją B,
znaczy to, że tandem nie jest lepszy od rozproszenia — a nie że „nic nie działa".

Rozbijanie motywu = **jedno podstawienie** w środku miejsca, powtarzane aż
motyw zniknie. Długość 800 pz zachowana, żadnych wstawek przesuwających ramkę.

---

## Kontrola po zbudowaniu

```
bramka Sędziego      18/20
dystans od dzikiego  110 / 123 / 147   (min/mediana/maks)
100 sekwencji, 0 odrzuconych, 0 duplikatów

blok   n   CCAAT śr   LRE śr   CreA śr
A     25      3.7      0.04     2.44
B     25      2.6      0.08     3.00
C     25      3.3      0.00     2.40
D     25      3.1      0.16     0.00
```

Interwencje zadziałały mechanicznie: blok C ma **zero** elementów świetlnych,
blok D **zero** miejsc CreA.

---

## Zastrzeżenie, które trzeba wypowiedzieć

**Blok C jest testem słabszym, niż zakładaliśmy.** Ziarna dekodera mają średnio
0,04–0,08 elementów świetlnych — czyli **dekoder i tak już je usunął**.
Rozbicie „zera" niewiele zmienia. Hipoteza świetlna jest więc na tej bazie
prawie niemierzalna.

Wynika z tego natomiast **hipoteza wyjaśniająca**, której wcześniej nie mieliśmy:
być może częścią powodu, dla którego ziarna dekodera biją dzikiego o pięć pozycji
(5,0 → 14,0), jest właśnie to, że **niszczą elementy represji świetlnej** obecne
w oryginalnym `pks1`. Dekoder nie „wie" o świetle — po prostu przepisuje
sekwencję w stronę typowego promotora rodzaju, a typowy promotor tych elementów
nie ma (mediana 0).

**Blok D jest za to interwencją realną.** Ziarna mają średnio 2,4–3,0 miejsc
CreA, czyli **więcej niż dziki (1)** — dekoder je dołożył. Usunięcie wszystkich
jest tu zmianą o wyraźnej wielkości i to blok D niesie najwięcej informacji.

---

## Czego się spodziewać i jak to odczytać

| wynik | wniosek |
|---|---|
| A lub C lub D > B | odpowiednia interwencja działa; kręcimy dalej tym parametrem |
| wszystkie ≈ B | architektura i represory nie mają znaczenia na tej bazie; oś CCAAT wyczerpana |
| wszystko < B | tandem szkodzi — wracamy do rozproszenia z `v8` |

Ponieważ TOP10 bierze dziesięć najlepszych ze stu, a każdy blok ma 25 sekwencji,
zwycięski blok powinien zdominować dziesiątkę.

---

## Wynik po wgraniu

| pole | wartość |
|---|---|
| TOP10 | **5** |
| ALL100 | **5** |
| punkty | **12,0** |

**Wniosek: żaden z trzech wariantów nie przebił kontroli.** Bloki A (tandem),
C (tandem + światło) i D (tandem + CreA) nie zdominowały dziesiątki najlepszych
— gdyby którykolwiek działał, TOP10 poszłoby w górę, bo każdy blok ma 25 z 100
sekwencji, a zwycięski blok zdominowałby TOP10.

Trzy hipotezy odpadają naraz:
- **architektura tandemowa nie jest lepsza od rozproszenia** — mimo że tak
  buduje się syntetyczne promotory grzybowe w literaturze;
- **zniesienie represji świetlnej** nie daje efektu (choć to był słaby test,
  patrz zastrzeżenie wyżej — ziarna już nie miały elementów świetlnych);
- **usunięcie CreA** nie daje efektu, mimo że była to interwencja realna
  (2,4–3,0 miejsc → 0).

`v8_ccaat` (ziarna + CCAAT rozproszone) pozostaje naszym najlepszym plikiem.
