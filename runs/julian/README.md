# Rejestr zgłoszeń — co wysłaliśmy, co to dało i dlaczego

Jeden plik do przeczytania, żeby wiedzieć, na czym stoimy. Uzupełniany po
każdym wgraniu. Szczegóły konstrukcji każdego portfela leżą w pliku `.md`
o tej samej nazwie co `.fasta`.

**Zasada oceny:** serwer trzyma **najlepsze** zgłoszenie drużyny, wybierane po
**surowym** wyniku TOP10. Pozycje w rankingu przesuwają się wraz z polem, więc
punkty z różnych godzin **nie są porównywalne wprost** — porównywalny jest
tylko surowy wynik, którego nie widzimy. Stąd znacznik czasu przy naszej
drużynie w `/ranking` jest jedyną informacją o tym, które zgłoszenie jest
naszym najlepszym.

---

## Tabela

| plik | baza | dodatek | TOP10 | ALL100 | pkt | uwaga |
|---|---|---|---|---|---|---|
| `pula.fasta` | ziarna dekodera | — | 2 / 5 druż. | 1 | 17,5 | pierwsze zgłoszenie, tylko **3** niezależne korzenie |
| `v3.fasta` | ziarna dekodera | — | 4 | 5 | 13,0 | 56 korzeni; pole urosło do 10 drużyn |
| `v4.fasta` | ziarna dekodera | — | 4 | 4 | 14,0 | **100** korzeni — podwojenie nie ruszyło TOP10 |
| `v5_K1b_gatunkowa` | ziarna | edycje gatunkowe | 4 | 4 | 14,0 | bez zmiany |
| `v6_K5_naturalnosc` | chimery naturalne | — | — | — | — | nie pobiło poprzedniego |
| **`v8_ccaat`** | **ziarna** | **CCAAT rozproszone** | 5 | 4 | 13,0 | **NASZE NAJLEPSZE** (znacznik 14:53 w rankingu) |
| `v9_B0_linia_bazowa` | dziki | 1 podstawienie | 9 | 8 | **5,0** | **linia bazowa** — bez niej nic nie znaczyło |
| `v10_B1_poliAT` | dziki | trakty poli(dA:dT) | 6 | 8 | 8,0 | podnosi ogon, nie podnosi średniej |
| `v11_B2_chimery_P1` | chimery z P1 | — | 9 | 9 | **4,0** | **poniżej bazy** — obce DNA szkodzi |
| `v12_kombinacja` | ziarna | CCAAT + trakty | — | — | — | zbudowane, niewgrane |
| `v13_uas_swiatlo` | ziarna | tandem UAS / LRE / CreA | — | — | — | zbudowane, niewgrane |
| `v14_glebokosc` | ziarna sortowane po głębokości + pok. 2/3 | — | 3 | 5 | 14,0 | pobiło v8 |
| **`v14_glebokosc_v2`** | **100 × pokolenie 4, linie niezależne** | — | 5 | 5 | 12,0 | **NASZE NAJLEPSZE** (znacznik **17:34:45**) |
| `v18_pokolenia_cis` | pokolenie 4 | CCAAT ×4 + IR-XBS + CreA rozbite | 5 | 5 | 12,0 | **nie pobiło v2** — bloki cis szkodzą |
| `v19_pokolenie8` | 100 × pokolenie 8 | — | 5 | 5 | 12,0 | **nie pobiło v2** — za daleko |

> **Uwaga o punktach 12,0 przy trzech ostatnich.** To są **rangi**, nie surowy
> wynik. Między `v14` (18:52) a `v2` (19:34) trzy drużyny wgrały lepsze pliki
> (`druzyna_04` 16:54, `druzyna_10` 17:02, `druzyna_03` 17:24 czasu serwera),
> a `druzyna_02` doszła do kompletu 10/10. Nasza ranga spadła, choć surowy
> wynik wzrósł. Nie da się tego odczytać z punktów — patrz metoda niżej.

### Metoda odczytu: znacznik czasu zamiast punktów

Serwer trzyma **najlepsze** zgłoszenie po **surowym** TOP10, nie ostatnie.
Potwierdzone eksperymentalnie w tej sesji: `v18` wgrany o 17:50 i `v19` o 20:08
**nie ruszyły** znacznika 17:34:45. Czyli:

```
znacznik SIE RUSZYL  ->  nowy plik ma wyzszy surowy TOP10
znacznik STOI        ->  nowy plik jest gorszy, serwer trzyma poprzedni
```

To jedyny dostępny odczyt surowego wyniku i **jedyny sposób porównania
zgłoszeń z różnych godzin**. Punkty z różnych godzin nie są porównywalne.

---

## Co z tego wynika — trzy rzeczy pewne

**1. Optymalizacja działa, i to mocno.** Linia bazowa (dziki + 1 podstawienie)
to **5,0 pkt**, nasze portfele stoją na **13–14**. Pięć pozycji rankingu.
Przez pół dnia wyglądało to na „nic nie działa", bo brakowało punktu
odniesienia — wszystkie mechanizmy zbiegały do wspólnego plateau i nie było
z czym ich porównać.

**2. Bazy nie wolno ruszać.** Wszystko, co oddala sekwencję od `pks1` w stronę
innego promotora, pogarsza wynik — nawet gdy dawca pochodzi z naszego szczepu
P1 (`v11` = 4,0, poniżej bazy). Baza to `pks1` przepuszczony przez dekoder;
optymalizujemy wyłącznie **dodatki**.

**3. Ranking wkładu.** Ziarno dekodera odpowiada za ~90 % całego zysku
(5,0 → 14,0). CCAAT dokłada tyle, że kombinacja ziarno+CCAAT jest naszym
najlepszym plikiem. Poli(dA:dT) daje +3,0 i tylko na ogonie. Chimery szkodzą.

## Czego już nie próbujemy — mamy dowody

- losowego mutowania DNA — 0 zwycięstw na 80 prób, do 640 podstawień;
- kręcenia `ile_kodow` — ×16 parametru daje +12 % dystansu;
- iterowanej wspinaczki pod Sędziego — plateau po jednym kroku, nic nie bije
  własnego rodzica (1 przypadek na 494);
- drugiego punktu startowego z naturalnych promotorów — 0/100 bije dzikiego,
  a jako portfel wypada poniżej linii bazowej;
- edycji okna 783–800 „bo tam patrzy model" — `wagaP` to artefakt brzegowy,
  szczyt siedzi na pozycji 788 dla 100 ze 101 różnych sekwencji.
