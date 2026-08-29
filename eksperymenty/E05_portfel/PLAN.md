# E05 · Portfel 100 sekwencji — dwanaście hipotez zamiast pięciu

**Status:** [OTWARTE] · **Zależy od:** E01–E04 · **Koszt:** ~150 wywołań + okno 5 min

---

## Matematyka, którą trzeba mieć z tyłu głowy

Dwie kategorie mierzą różne rzeczy i nagradzają różne strategie:

- **ALL100** = suma / 100 (dzielnik stały) → to **średnia**. Jedna słaba
  sekwencja kosztuje 1/100.
- **TOP10** = suma dziesięciu najlepszych / 10 → to **statystyka pozycyjna**.
  Słaba sekwencja nie kosztuje **nic**. Nagradza prawy ogon.
- Serwer wybiera najlepsze zgłoszenie drużyny **po TOP10**.
- Punktacja jest **rangowa wśród pięciu drużyn**: 10 / 7,5 / 5 / 2,5 / 0.

Z tego wynikają dwie rzeczy, których faza 1 nie wykorzystała.

**Po pierwsze: ALL100 jest już nasycone.** Jesteśmy na pozycji 1. Przy pięciu
drużynach skala ma pięć poziomów, więc podnoszenie średniej nie może już nic
dać — może tylko chronić przed spadkiem. Marginalna wartość każdej sekwencji
„dla średniej" jest bliska zeru.

**Po drugie: skorelowane zakłady to jedno losowanie.** Symulacja z komórki 34
fazy 1 pokazuje, że ryzyko podnosi TOP10 — ale zakłada, że ryzykowne sekwencje
są **niezależnymi** losowaniami. Blok „20 × TATAAA z jitterem" to jedna
hipoteza powtórzona dwadzieścia razy: jeśli hipoteza jest zła, pada cały blok.
Statystyka pozycyjna widzi wtedy jedno losowanie, nie dwadzieścia.

> **Wniosek: liczy się liczba niezależnych hipotez, nie liczba sekwencji.**
> Stąd 12 bloków po 8 zamiast 5 po 20–30. Wewnątrz bloku **skan parametru**
> (TATAAA na 722, 726, 730 … 766), nie szum wokół jednego punktu — skan jest
> jednocześnie bardziej różnorodny i bardziej informatywny.

## Skład portfela

Budżet przydzielany warunkowo, w zależności od werdyktów E01–E04.
`portfel.py` czyta `wyniki.json` każdego eksperymentu i sam przesuwa sztuki.

| # | blok | ile | hipoteza | zależy od |
|---|---|---|---|---|
| 1 | rdzeń rodziny `hybryda` | 12 | zabezpieczenie ALL100 — wiemy, że daje pozycję 1 | — |
| 2 | gatunkowy, punkt stały | 8 | W7: jedyna potwierdzona hipoteza fazy 1 | — |
| 3 | gatunkowy × okolica (mutacje tylko na pozycjach swobodnych) | 8 | okolica punktu stałego | — |
| 4 | najlepsza komórka E04 + repliki | 10 | zwycięzca planu faktorialnego | E04 |
| 5 | druga i trzecia komórka E04 | 8 | ubezpieczenie na wypadek szumu w E04 | E04 |
| 6 | CreA rozbite, 4 warianty podstawienia × 2 tła | 8 | derepresja kataboliczna — wymiar niewidoczny dla Sędziego | — |
| 7 | rdzeń z konsensusu E03, skan 4 pozycji wstawienia | 8 | element rdzeniowy ze stu naturalnych promotorów | E02, E03 |
| 8 | TATAAA, skan okna 720–770 co 6 pz | 8 | brak kanonicznego TATA w −80…−30 (H1 + motywy) | — |
| 9 | chimery dziki × naturalny | 8 | prawdziwe DNA po obu stronach cięcia | E03 |
| 10 | naturalne promotory bez zmian (jeśli któryś bije) | 6 | drugi punkt startowy | E03 |
| 11 | dekoder poziom 0, `ile_kodow` 16 | 8 | maksymalny dystans osiągalny w latencie | — |
| 12 | odloty: sonda Goodharta (przesycone TATA), test `N` w pozycjach o zerowym gradiencie, kombinacje wszystkiego naraz | 8 | loteryjne bilety — kosztują 1/100 średniej, nie kosztują nic w TOP10 | — |

Razem 100. Bloki 4, 5, 7, 9, 10 kurczą się, gdy odpowiedni eksperyment nie
został uruchomiony; nadmiar idzie do bloku 1 (bezpieczna średnia) i bloku 12
(ogon).

## Dwie sondy diagnostyczne w bloku 12

Warto je wysłać, nawet jeśli są niemal na pewno słabe, bo **kosztują 1 % średniej
i nie kosztują nic w TOP10**, a odpowiadają na otwarte pytania z briefu:

- **Sonda Goodharta** (pytanie z sekcji 6): sekwencja naszpikowana kilkunastoma
  TATA-boxami. Jeśli Sędzia ją kocha, a ranking nie drgnie — mamy udokumentowany
  rozjazd proxy i gotowy slajd.
- **Sonda `N`** (otwarte pytanie 3): 80 `N` (dokładnie 10 %, próg) wstawionych
  w pozycje o `wagaP` < 0,05. `N` wchodzi do modelu jako 0,25 w każdym kanale.
  Czy jest neutralne, czy szkodzi? Nietestowane, tanie.

## Protokół zgłoszenia

```bash
python eksperymenty/E05_portfel/portfel.py -o runs/julian/v2.fasta
python -m hyppe waliduj runs/julian/v2.fasta        # 100 do oceny, 0 odrzuconych
python -m hyppe me                                   # zgloszenie_mozliwe_za_s
python -m hyppe wgraj runs/julian/v2.fasta --dry-run
python -m hyppe wgraj runs/julian/v2.fasta
python -m hyppe ranking
```

Zgłoszenie **niczym nie ryzykuje** — liczy się najlepszy wynik drużyny, nie
ostatni. Słabsze zgłoszenie kosztuje wyłącznie okno pięciu minut.

## Atrybucja blokowa — jak wycisnąć więcej niż jeden bit

Wyrocznia zwraca dwie rangi przy pięciu drużynach, więc jedno zgłoszenie niesie
około jednego bitu. Ale przy **kilku** zgłoszeniach da się z tego coś wyciągnąć,
jeśli zaprojektuje się je jak eksperyment:

1. Trzon 40 sekwencji (bloki 1–3) **zostaje bez zmian** we wszystkich zgłoszeniach.
2. W każdym zgłoszeniu wymieniamy jeden blok testowy na inny.
3. Zmiana pozycji TOP10 jest sygnałem o tym bloku.

Ograniczenia trzeba wypowiedzieć wprost: przy pięciu drużynach ranga ma pięć
poziomów, więc to jest **porównanie porządkowe, nie pomiar**. Jeśli
konkurencja wgrywa w tym samym czasie, sygnał jest skażony. To jest najlepsza
dostępna atrybucja, a nie dobra atrybucja — i tak trzeba to opisać przy Jury.

Etykiety w nagłówkach FASTA (`E04_A1B0C1D1_r02`, `blok07_rdzen_skan_742`)
niosą pochodzenie, więc po każdym zgłoszeniu wiadomo, co dokładnie było w środku.

## Kolejność zgłoszeń, jeśli starczy okien

| # | co zmieniamy | pytanie |
|---|---|---|
| 2 | pełny nowy portfel (12 bloków) | czy różnorodność podnosi TOP10 względem jednorodnej puli? |
| 3 | blok 7 (rdzeń) → więcej bloku 2 (gatunek) | czy rdzeń w ogóle działa? drugi tor kontroli dla E02 |
| 4 | blok 12 (odloty) → repliki najlepszej komórki E04 | czy ogon bierze się z ryzyka, czy z najlepszej kombinacji? |

## Kryteria decyzyjne

| obserwacja po wgraniu | wniosek |
|---|---|
| TOP10 rośnie, ALL100 spada | różnorodność działa zgodnie z przewidywaniem — kontynuować |
| TOP10 rośnie, ALL100 zostaje | najlepszy możliwy wynik — bloki są jednocześnie mocne i różne |
| TOP10 bez zmian, ALL100 spada | zakłady są słabe, nie tylko ryzykowne — wrócić do trzonu i szukać w E04 |
| oba spadają | sprawdzić raport filtrowania w `runs/ostatnie_wgranie.json`; to zwykle problem walidacyjny, nie biologiczny |

## Zastrzeżenia

- Rangi zależą od tego, co robią pozostałe drużyny. Spadek pozycji nie musi
  znaczyć, że nasze zgłoszenie jest gorsze.
- Model nie był walidowany laboratoryjnie. Wynik to predykcja modelu, nie
  aktywność mokra — i tak trzeba to powiedzieć na prezentacji.
- Blok 12 celowo zawiera sekwencje, które uważamy za słabe. To jest decyzja
  wynikająca z asymetrii punktacji, a nie niedopatrzenie.
