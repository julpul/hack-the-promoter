# E14 — wnioski: co faktycznie niesie wynik

Dokument decyzyjny. Jedno kryterium: **czy zgłoszenie pobiło nasze własne
14,0 z v14.** Wszystko poniżej zmierzone w tym samym polu rankingowym
(2026-08-29, 18:52–20:00 czasu lokalnego), więc punkty są porównywalne
między sobą — czego nie da się powiedzieć o zgłoszeniach z pierwszej
połowy dnia.

---

## 1. Tabela pomiarów

| plik | konstrukcja | `blad_odtworzenia` | dystans od dzikiego | pkt |
|---|---|---|---|---|
| **`v14_glebokosc`** | 45 głęb. + 45 pokoleń + 10 kontroli | A: 9–17–19 · B: 0–4–9 | B: 123–142–171 | **14,0** |
| `v15_czysta_glebokosc` | 100 × najgłębsze z puli 603 | 10–17 | ~100–150 | 12,0 |
| `v16_mieszanka_podkrecona` | 45 głęb. + 45 pokoleń z **głębokich** ziaren | A: 10–17 · B: 0–5–11 | B: **192–262** | 11,0 |
| `w18_piec_rodzin` | 5 rodzin × 20, w tym kompozyty cis | mieszane | mieszane | 12,0 |
| `v22_pas_optymalny` | 100 × izolowana rodzina B, twardy pas dystansu | 0–2–4 | 123–149–176 | 12,0 |
| `w21_cbh1` | v14 + CCAAT ×4 + Cre1 rozbite | — | +~24 | *(w kolejce)* |
| `w17_pelna_kompozycja` | v14 + wszystkie cztery bloki | — | +~75 | *(w kolejce)* |
| `w20_tylko_xbs` | v14 + IR-XBS ×2 | — | +~44 | *(w kolejce)* |
| `w19_pivot_naturalny` | naturalny podkład + wszystkie bloki | 63–95 | ~600 | *(w kolejce)* |

---

## 2. Trzy hipotezy, które te liczby zabijają

### 2.1 „Głębiej na rozmaitości = lepiej" — **fałsz**

To była teza `v14_glebokosc.md` i wyglądała na potwierdzoną, bo v14 dał +2,0.
Ale v15 wziął **tę samą regułę doprowadzoną do końca** — 100 najgłębszych
z puli 4× większej, `blad` 10–17 zamiast 9–19 — i spadł do 12,0.

Zysk v14 nie pochodził z tego, że posortowaliśmy po głębokości. Pochodził
z czegoś, co sortowanie po głębokości **przypadkiem przyniosło razem ze sobą**.

### 2.2 „Dalej wzdłuż osi dekodera = lepiej" — **fałsz**

v16 to v14 z blokiem B pchniętym z dystansu 123–171 na 192–262. Spadek do
11,0 — najgorszy wynik dnia. Granica jest ostra i leży w okolicy **~180 pz**
od dzikiego. Powyżej niej sekwencja przestaje być wariantem `pks1`.

To spina się z `v11_B2_chimery_P1` (dystans 300+, wynik 4,0, poniżej linii
bazowej). Dwa niezależne pomiary tej samej ściany.

### 2.3 „Więcej rodzin w portfelu = lepiej" — **fałsz**

`w18` miał pięć rodzin po 20 sztuk, w tym trzy z zainstalowanymi blokami cis.
12,0. Różnorodność sama w sobie nie jest walutą — to była moja hipoteza po
v15 i była zła.

---

## 3. Czwarta hipoteza — koniunkcja — też upadła

Po odjęciu trzech powyższych został jeden opis pasujący do wszystkich
pomiarów:

> Punkty niesie rodzina o **`blad_odtworzenia` bliskim zeru** *przy jednoczesnym*
> **dystansie 120–180 pz** od dzikiego. v14 miał jej 45 sztuk. v15 nie miał jej
> wcale. v16 miał ją, ale wypchniętą poza pas dystansu.

Głębokość i dystans osobno nie działają (2.1, 2.2), więc koniunkcja była
jedynym, co zostało. `v22_pas_optymalny` zbudowaliśmy dokładnie pod to
zdanie: 100 sekwencji, `blad` 0–2–4, dystans 123–176 — trafienie w pas
lepsze niż w samym v14 (0–4–9 / 123–171).

**v22 dał 12,0.** Hipoteza koniunkcji upada razem z trzema poprzednimi.

### Co z tego wynika naprawdę

Cztery niezależne próby zrekonstruowania „przepisu na v14" — po głębokości,
po dystansie, po różnorodności i po koniunkcji — dały **12,0 / 11,0 / 12,0 /
12,0**. Żaden pojedynczy opis wyciągnięty z v14 nie odtwarza jego wyniku
po wyizolowaniu.

Zostają dwie możliwości i nie umiemy ich rozdzielić posiadanymi narzędziami:

1. **v14 był szczęśliwym losowaniem.** Przy rankingu opartym na randze
   różnica 12 → 14 to dwie rangi w polu dziesięciu drużyn; przy jednym
   pomiarze na wariant to mieści się w szumie.
2. **Nośnikiem jest sama heterogeniczność konkretnej mieszanki**, której nie
   da się opisać żadną z osi, jakie umiemy zmierzyć (`blad_odtworzenia`,
   dystans Hamminga, liczba rodzin) — bo Wyrocznia patrzy na coś, czego
   nie mamy.

Uczciwie: **nie odróżniamy tych dwóch przypadków.** Żeby to zrobić, trzeba
by powtórzyć przepis v14 z innymi ziarnami i zobaczyć, czy wraca 14,0 —
to jeden test replikacyjny, którego nie zdążyliśmy zrobić przed wygaśnięciem
klucza. To jest pierwsza rzecz do zrobienia, gdyby projekt miał ciąg dalszy.

---

## 4. Bloki cis z `PIVOT.md` — status

Cztery bloki (CCAAT ×4, IR-XBS, poli(dA:dT), rozbicie Cre1) są zaimplementowane
w `strategie.py` jako funkcje niezależne od podkładu i przetestowane offline
(podkład v14 miał CCAAT=0 i GGCTAA=0, po złożeniu 4 i 4 — zgodnie z §3.4
pivota). Cztery zgłoszenia rozdzielają czynniki:

| plik | czynnik | co rozstrzyga |
|---|---|---|
| `w21_cbh1` | CCAAT + Cre1 | przepis z `cbh1` (represor precz, aktywator na miejsce) |
| `w20_tylko_xbs` | IR-XBS | element o największym udokumentowanym efekcie |
| `w17_pelna_kompozycja` | wszystko | czy bloki się sumują |
| `w19_pivot_naturalny` | podkład | pivot dosłownie, z naturalnym DNA |

**Uwaga metodyczna, którą trzeba wypowiedzieć przed odczytem:** każdy blok
oddala sekwencję od dzikiego (w21 +~24 pz, w20 +~44, w17 +~75), a §2.2 mówi,
że powyżej ~180 pz wynik się załamuje. Podkład v14 leży na ~100–170, więc
`w17` z +75 **wychodzi poza pas z samej arytmetyki**. Jeśli w17 wypadnie
najgorzej z całej czwórki, to nie będzie dowód przeciw biologii bloków —
tylko powtórzenie pomiaru 2.2. Czysty test biologii to `w21` (najmniejszy
przyrost dystansu).

---

## 5. Decyzja: co robić z pozostałym czasem

Klucz API wygasa **20:15**. Realnie zostają 3–4 okna wgrania.

1. **Zabezpieczone:** v14 = 14,0 leży na serwerze i nic go nie zdejmie —
   serwer trzyma najlepsze po surowym TOP10, potwierdzone tym, że `v11` (4,0)
   i `v16` (11,0) nie ruszyły naszego znacznika w rankingu.
2. **Jeśli v22 > 14,0** → opis z §3 jest trafny. Wtedy jedyne sensowne
   dokręcanie to zawężenie pasa (np. 130–165) i ponowny przesiew — nie nowe osie.
3. **Jeśli v22 ≤ 14,0** → koniunkcja też nie tłumaczy v14. Zostaje wniosek
   uczciwy i niewygodny: **przy tym poziomie szumu rankingowego różnice 11–14
   punktów to 1–3 rangi i nie odróżniamy sygnału od losu.** Wtedy zostawiamy
   v14 i nie ryzykujemy.
4. **Bloki cis** rozstrzygną się same w oknach 19:44–20:00. Cokolwiek pokażą,
   `strategie.py` zostaje jako jedyna część projektu, w której coś
   **zaprojektowaliśmy** zamiast losować — i to jest materiał na obronę
   przed Jury niezależnie od punktów.

---

## 6. Czego ten dokument nie rozstrzyga

- **Nie wiemy, co mierzy Wyrocznia.** Cała analiza jest na poziomie „która
  rodzina dostaje więcej punktów", bez dostępu do metryki.
- **Nie mamy powtórzeń.** Każdy wariant wgrany raz. Przy rankingu opartym
  na randze różnica 1 punktu może być szumem pola, a nie naszej sekwencji.
  Uczciwy odczyt to tylko kolejność: 14 > 12 ≈ 12 > 11.
- **Nie testowaliśmy pasa poniżej 120 pz.** Cały zakres 1–100 pz jest u nas
  pokryty jedynie linią bazową (`v9_B0`, 1 podstawienie, 5,0 pkt).
  Gdyby był czas, to jest pierwsza dziura do zamknięcia.
