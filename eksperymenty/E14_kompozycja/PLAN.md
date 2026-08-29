# E14 — pivot po v14: co z kompozycji zostaje, a co właśnie upadło

**Napisane:** 2026-08-29 18:57, po wgraniu `v14_glebokosc` (14,0 pkt, TOP10 ranga 3).

---

## 0. Sprostowanie do `PIVOT.md` — dwa z trzech filarów już nie stoją

`PIVOT.md` napisaliśmy, gdy sześć kolejnych zgłoszeń siedziało w paśmie 12–14.
Diagnoza brzmiała: „sufit metody jest zmierzony, perturbacja wyczerpana,
trzeba zmienić przestrzeń". **v14 pokazał, że to była zła diagnoza.**

| filar `PIVOT.md` | stan po v14 |
|---|---|
| „Sufit metody jest zmierzony. 3 → 56 → 100 ziaren, TOP10 nie drgnął" | **obalony.** Ten sam mechanizm, ziarna posortowane po `blad_odtworzenia` zamiast brane z bramki: +1 ranga TOP10, +1 ranga ALL100, +2,0 pkt |
| „Cała nasza eksploracja to jedna okolica" | **prawdziwy, ale nieszkodliwy.** Okolica jest jedna — tylko nigdy nie szukaliśmy w niej najgłębszego punktu, braliśmy pierwszy lepszy |
| „Nie mamy problemu z próbkowaniem" | **obalony.** Mieliśmy dokładnie problem z próbkowaniem: bramka binarna zamiast szeregowania |

Nie było sufitu metody. Był sufit **naszego doboru próbki**.

## 0.1. I trzeci filar: mechanizm pivota przewiduje odwrotnie niż zmierzyliśmy

To jest najważniejsze zdanie w tym dokumencie.

`PIVOT.md` §4 uzasadnia prawdziwy podkład tak: *„`blad_odtworzenia` wraca do
63–95 zamiast 16–27 — jeśli Wyrocznia była trenowana na prawdziwych
promotorach, wychodzimy z poza-rozkładu"*. Czyli: **bliżej naturalnego = lepiej.**

v14 przesunął nas w **przeciwną** stronę i to dało punkty:

```
prawdziwe DNA            blad_odtworzenia  63 – 95
nasze stare ziarna                         13 – 21 – 34
v14, blok A (45 szt.)                       9 – 19      <- najdalej od naturalnego
                                                            i najlepszy wynik, jaki mamy
```

Kierunek „w stronę naturalnego" był już zresztą mierzony wprost i przegrał:

| zgłoszenie | co to było | wynik |
|---|---|---|
| `v9_B0` | dziki + 1 podstawienie | 5,0 — linia bazowa |
| `v6_K5` | chimery naturalne | nie pobiło poprzedniego |
| `v11_B2` | chimery z prawdziwego P1 | **4,0 — poniżej linii bazowej** |

Trzy niezależne pomiary w tę samą stronę. **Hipoteza „prawdziwy podkład jest
lepszy" nie jest nieprzetestowana — ona jest przetestowana i fałszywa.**

**Wniosek:** z pivota zostaje **biologia bloków**, wypada **podkład**.
Bloki instalujemy na ziarnie dekodera, nie na naturalnym promotorze.

---

## 1. Co z pivota zostaje w mocy

Argument z `PIVOT.md` §3.4 jest nadal dobry i niezależny od tego, co upadło:

| element | rola | dziki | mediana nat. | percentyl dzikiego |
|---|---|---|---|---|
| **CCAAT** (Hap2/3/5) | aktywator ogólny | **0** | 2 | **0 %** |
| **GGCTAA** (Xyr1/ACE2) | aktywator | **0** | 0 | **0 %** |
| SYGGRG (Cre1) | **represor** | 2 | 2 | 40 % |
| trakt A/T ≥ 8 pz | NDR | 3 | 5 | 42 % |

Dwa elementy o percentylu 0 % to nadal najlepiej uzasadnione biologicznie
miejsca do ruszenia, a literatura (`cbh1`: 5,0 × i 3,6 ×; `xyn1` IR-XBS;
`AOX1` poli(dA:dT) 0,25–3,5 ×) daje im nazwy białek. To broni się przed Jury
i to jest jedyna część projektu, w której cokolwiek **projektujemy**.

Zmienia się tylko **na czym** je instalujemy.

---

## 2. Dwa pytania, na które E14 ma odpowiedzieć

### P1 — atrybucja v14: głębokość czy pokolenia?

v14 zmieszał trzy bloki (A = 45 głębokich, B = 45 z dalszych pokoleń,
K = 10 kontroli). Zysk +2,0 może pochodzić z A, z B albo z obu.
Bez rozdzielenia nie wiemy, co pchać dalej.

**To jest najtańszy i najpewniejszy punkt na liście.** Dwa zgłoszenia po
100 sekwencji każde, czyste bloki.

### P2 — czy bloki cis dokładają cokolwiek na głębokim ziarnie?

`v8_ccaat` (CCAAT na płytkich ziarnach) siedział w paśmie 12–14, czyli
w szumie. Ale testowaliśmy go na **losowej** próbce ziaren. Na ziarnach
z ogona rozkładu — z `blad_odtworzenia` 9–14 — dodatek może zachować się
inaczej, bo baza jest inna.

---

## 3. Plan zgłoszeń

Wgrania są darmowe — serwer trzyma **najlepsze** po surowym TOP10
(potwierdzone: `v11_B2` dał 4,0 i nasz znacznik w rankingu się nie ruszył).
Każde wgranie jest więc czystym pomiarem bez ryzyka.

| # | plik | zawartość | pytanie |
|---|---|---|---|
| **v15** | `v15_czysta_glebokosc.fasta` | 100 × najgłębsze z przesiewu 6400 losowań | ile daje sama głębokość, do końca? |
| **v16** | `v16_czyste_pokolenia.fasta` | 100 × drugie/trzecie pokolenie | ile dają same pokolenia? |
| **v17** | `v17_glebokosc_bloki.fasta` | v15 + CCAAT ×4 + IR-XBS + poli(dA:dT) + rozbite Cre1 | czy biologia dokłada do głębokości? |

v15 vs v16 odpowiada na P1. v15 vs v17 odpowiada na P2 — i to jest ta sama
konstrukcja kontrolna, którą `PIVOT.md` proponował dla podkładu (v9 vs v11),
tylko przeniesiona na oś, która faktycznie działa.

### Czego świadomie nie robimy

- **Nie budujemy na naturalnym podkładzie.** Trzy pomiary mówią, że to szkodzi
  (§0.1). Gdyby został czas po v15–v17, jedno zgłoszenie kontrolne domknęłoby
  temat — ale nie kosztem osi, która działa.
- **Nie używamy Sędziego do selekcji**, tylko jako bramki wejściowej.
  Wysycony (0/100 naturalnych, 0/80 losowych, plateau po 1 kroku); w v14
  zignorowaliśmy go przy szeregowaniu i dokładnie dlatego wyszło.
- **Nie ruszamy rdzenia −50…0.** Log-odds dzikiego wobec PWM ze stu
  naturalnych: 3,67 przy medianie 2,97 (percentyl 52 %) — nie ma tam czego
  naprawiać.

---

## 4. Jak odczytać wynik

| obserwacja | wniosek | co dalej |
|---|---|---|
| v15 > v16 | działa **głębokość** | przesiewać agresywniej, brać skrajniejszy kwantyl |
| v16 > v15 | działa **dystans wzdłuż osi dekodera** | czwarte i piąte pokolenie |
| v15 ≈ v16 ≈ 14,0 | oba bloki dały tyle samo — zysk v14 jest z **liczby** dobrych sekwencji, nie z ich rodzaju | dopełniać portfel najlepszymi z obu |
| v17 > v15 | biologia dokłada **na głębokiej bazie** | pełny plan czynnikowy z `PIVOT.md` §4, ale na ziarnach |
| v17 < v15 | bloki cis psują prototypowość | zamknięcie tematu CCAAT/XBS, cała reszta czasu na głębokość |

Ostatni wiersz jest wartościowy tak samo jak pierwszy: zamknąłby oś, na którą
poszły `v8`, `v12` i `v13`, i zwolnił czas.
