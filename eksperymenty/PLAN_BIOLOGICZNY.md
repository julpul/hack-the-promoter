# Zatrzymanie i przemyślenie — plan biologiczny

**2026-08-29, po siedmiu zgłoszeniach** · dokument decyzyjny, nie sprawozdanie

---

## 1. Centralny fakt: wszystko daje ten sam wynik

| # | plik | mechanizm | ile zmienia wobec dzikiego | TOP10 | ALL100 |
|---|---|---|---|---|---|
| v1 | `pula.fasta` | dekoder, 3 korzenie | ~100 pz | 2 / 5 druż. | 1 / 5 |
| v3 | `v3.fasta` | dekoder, 56 korzeni | ~100 pz | **4** | 5 |
| v4 | `v4.fasta` | dekoder, 100 korzeni | ~100 pz | **4** | 4 |
| v5 | `v5_K1b` | dekoder + gatunek | ~104 pz | **4** | 4 |
| v6 | `v6_K5` | chimery z prawdziwym DNA | ~300–600 pz | ≤ v5 | — |
| v8 | `v8_ccaat` | wstawione boksy CCAAT | **5–15 pz** | **5** | 4 |

**Siedem zgłoszeń, sześć różnych mechanizmów, jeden wynik.** Zmienialiśmy od
**5 pz** (CCAAT) przez **100 pz** (dekoder) po **600 pz** (chimery) — trzy rzędy
wielkości — i ranking nie drgnął.

To jest najważniejsza obserwacja całego projektu i wymaga wyjaśnienia,
zanim wygenerujemy cokolwiek nowego.

## 2. Trzy możliwe wyjaśnienia — i jak je rozróżnić

**W1. Wyrocznia jest niewrażliwa na to, co zmieniamy.** Wszystkie nasze
sekwencje są pochodnymi jednego promotora `pks1`. Być może ocena zależy
głównie od cechy, której w ogóle nie ruszamy.

**W2. Poprawiamy się, ale instrument tego nie pokazuje.** Punktacja jest
**rangowa wśród dziesięciu drużyn**, krok skali to 1 punkt. Realna poprawa
mniejsza niż jedna pozycja jest **niewidoczna**. Nie mamy dostępu do surowych
ocen — widzimy tylko miejsce.

**W3. Liderzy robią coś kategorialnie innego.** Trzy drużyny stoją na 18 pkt,
my na 13–14. To nie jest przewaga o włos.

> **Rozróżnia je jeden brakujący pomiar.**

## 3. Czego nam brakuje: linii bazowej

**Nigdy nie wysłaliśmy dzikiego promotora.**

Nie wiemy, ile punktów dostaje punkt wyjścia. Bez tego nie wiemy, czy
którakolwiek z siedmiu prób cokolwiek poprawiła — może wszystkie są **gorsze**
od nietkniętego `pks1`, a może wszystkie lepsze i po prostu tego nie widać.

To jest dokładnie ta sama klasa błędu, którą sami złapaliśmy w E06
(krzyżowanie przegranych) i E07 (niezbalansowany przesiew): **wniosek bez
kontroli**. Tylko tym razem brakuje kontroli najbardziej podstawowej.

> **B0 — pierwszy ruch, priorytet bezwzględny.** Portfel 100 sekwencji
> minimalnie różniących się od dzikiego (po 1–3 podstawienia, tylko po to,
> żeby przejść filtr unikalności). Odczyt mówi wprost, czy jesteśmy powyżej
> czy poniżej startu. Koszt: jedno okno.

## 4. Czego nigdy nie ruszaliśmy

| oś | nasze sekwencje | naturalne promotory | status |
|---|---|---|---|
| GC całości | 47–50 % (zawsze) | **17 % – 61 %** | nietknięte |
| GC proksymalne (−200…0) | 44 % | 14 % – 68 % | nietknięte |
| trakty poli(dA:dT) ≥ 6 pz | **0** | 0–10, u 40 % promotorów | nietknięte |
| pochodzenie | zawsze pochodna `pks1` | — | nietknięte |

Wszystkie nasze portfele siedzą w jednym punkcie przestrzeni składu
nukleotydowego. Zmienialiśmy **motywy** i **tożsamość zasad**, nigdy
**architekturę**.

## 5. Hipoteza biologiczna, która wynika z tej luki

### B1 · Region wolny od nukleosomów (poli-dA:dT)

**Mechanizm.** DNA w komórce jest nawinięte na nukleosomy. Promotor, który jest
zajęty przez nukleosom, jest niedostępny dla polimerazy. Odcinki
homopolimerowe **poli(dA:dT)** są sztywne i mają wewnętrzną krzywiznę, przez co
**energetycznie nie nadają się do owinięcia wokół histonów**. Geny o wysokiej
ekspresji konstytutywnej u drożdży i grzybów strzępkowych mają charakterystyczny
**NFR (nucleosome-free region)** tuż przed miejscem startu, utrzymywany właśnie
przez takie trakty.

**Dane.** `pks1` ma **zero** traktów ≥ 6 pz. W zbiorze naturalnym ma je 40 %
promotorów, do dziesięciu sztuk, najdłuższy 27 pz.

**Dlaczego to jest inna klasa zmiany niż wszystko dotąd.** CCAAT to rekrutacja
konkretnego czynnika — zmiana 5 pz, sygnał punktowy. Poli(dA:dT) to zmiana
**fizycznej dostępności** promotora: działa niezależnie od tego, jakie czynniki
są obecne, i wymaga zmiany kilkudziesięciu zasad w sposób, który przesuwa też
skład nukleotydowy. To jednocześnie hipoteza mechanistyczna **i** ruch na osi
składu, której nigdy nie dotknęliśmy.

**Dlaczego akurat teraz.** Model przewiduje ekspresję z danych ekspresyjnych.
Takie modele opierają się w dużej mierze na **statystyce k-merów**, a nie na
pojedynczych miejscach wiązania. Wstawienie 5 pz CCAAT nie rusza statystyki
k-merów. Wstawienie kilku traktów po 10–20 pz — rusza.

### B2 · Chimery z promotorami tego samego szczepu

W zbiorze jest **pięć promotorów z *Trichoderma atroviride* P1** — dokładnie
naszego szczepu (`P1_G007739`, `P1_G002074`, `P1_G005351`, `P1_G006612`,
`P1_G002582`, GC 38–61 %). Wyrocznia ocenia **w kontekście P1**.

Chimery z tymi pięcioma to jedyne sekwencje, w których obie części pochodzą
z tego samego repertuaru czynników transkrypcyjnych co gen docelowy. W v6
traktowaliśmy wszystkie sto naturalnych jednakowo i utopiliśmy te pięć w tłumie.

### B3 · Derepresja kataboliczna

`pks1` ma miejsce CreA na −240. CreA wycisza geny w obecności glukozy.
Rozbicie tego miejsca to **usunięcie hamulca**, a nie dodanie gazu — działa
w wymiarze, którego żaden z naszych mierników nie widzi.

Uczciwie: dziki ma tego motywu tyle, co typowy promotor (mediana 1), więc to
nie jest anomalia. Ale mechanizm jest dobrze udokumentowany i jest to **jedyna
hipoteza o usunięciu negatywnej regulacji** — wszystkie pozostałe dodają.

## 6. Kolejność

| # | co | po co | koszt |
|---|---|---|---|
| **B0** | 100 kopii dzikiego (±1–3 pz) | **linia bazowa** — bez niej nie wiemy nic | 1 okno |
| **B1** | poli(dA:dT), 2–8 traktów po 10–25 pz | architektura chromatyny, oś składu | 1 okno |
| **B2** | chimery z 5 promotorami P1 | jedyny materiał z naszego szczepu | 1 okno |
| **B3** | CreA rozbity ± B1 | usunięcie represji | 1 okno |

**B0 jest bezwarunkowo pierwsze.** Jeśli okaże się, że dziki sam w sobie daje
tyle samo co nasze najlepsze zgłoszenie, to znaczy, że siedem prób nie zrobiło
nic — i cała dalsza praca musi iść w kierunku zmian **większych**, a nie
subtelniejszych. Jeśli dziki wypada gorzej, mamy dowód, że optymalizacja
działa, tylko instrument jest zbyt zgrubny, żeby pokazać ile.

## 7. Co to zmienia w narracji na prezentację

Ta sekcja jest wartościowa **niezależnie od punktów**.

Mamy udokumentowany przypadek, w którym **siedem różnych strategii
optymalizacyjnych daje identyczny wynik pomiarowy** — od edycji 5-zasadowych po
przebudowę 600 zasad. To prowadzi do pytania metodologicznego, które jest
ciekawsze od samego rankingu:

> *Czy mierzymy właściwość sekwencji, czy rozdzielczość instrumentu?*

Do tego dochodzą trzy kontrole, które obaliły nasze własne wnioski (E02 —
`wagaP` jako artefakt brzegowy; E06 — operator kontra dziedziczenie; E07 —
trend z niezbalansowanej próby) i jedna luka, którą sami u siebie znaleźliśmy
(brak linii bazowej). To jest opowieść o **metodzie**, nie o szczęściu
w losowaniu ziarna.
