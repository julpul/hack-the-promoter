# E07 · Przesiew — gdzie w przestrzeni dekodera siedzą zwycięzcy

**Status:** [OTWARTE] · **Zależy od:** E06 · **Blokuje:** zgłoszenie · **Koszt:** ~450 wywołań, 4 min

---

## Co wynika z E06

| ramię | bije dzikiego | bije własnego rodzica |
|---|---|---|
| surowe `/edycje` | 0 / 16 | — |
| krzyżówka **przegranych** | **0 / 16** | 0 / 16 |
| krzyżówka **zwycięzców** | 9 / 16 (56 %) | 0 / 16 |
| zwycięzca × dziki | 8 / 16 (50 %) | 0 / 16 |
| **mutacja** zwycięzcy o ten sam dystans | 8 / 16 (50 %) | 0 / 16 |
| drugie pokolenie | 11 / 16 (69 %) | 0 / 16 |

Trzy zdania, które z tego wynikają:

1. **Operator nie ma znaczenia.** Krzyżowanie (56 %) i zwykła mutacja o ten sam
   dystans (50 %) dają to samo. Rekombinacja nie wnosi nic ponad „zacznij od zwycięzcy".
2. **Rodzic ma znaczenie całkowite.** Krzyżowanie przegranych: 0/16.
3. **Nic nigdy nie bije własnego rodzica.** 0 na 80 sekwencji, we wszystkich ramionach.

Razem: **cała nasza optymalizacja to loteria na etapie losowania ziarna**, a to,
co po niej robimy, jedynie kopiuje ziarno z połowicznym powodzeniem. Skoro
potomek nigdy nie przewyższa rodzica, jedyną drogą w górę jest **znalezienie
lepszego ziarna**, a jedyną drogą do TOP10 — znalezienie **wielu niezależnych** ziaren.

## Dlaczego to jest właściwe pytanie akurat teraz

Wgrane zgłoszenie (`pula.fasta`) ma 39 sekwencji przechodzących bramkę, ale
36 z nich to rodzina `hyb_*` — dzieci **trzech** zwycięzców z jednego zaciągu.
W kategorii TOP10, która jest statystyką pozycyjną, to są **trzy niezależne
losowania**, a nie trzydzieści sześć. Dokładnie to diagnozował W8 („jedna
rodzina powtórzona sto razy"), tylko wtedy nie było wiadomo, że rodzina ma
korzeń w trzech sekwencjach.

Nikt nie zmierzył, skąd te trzy się wzięły. `pula_nawigator` chodzi po
`ile_kodow = 6 + runda` przy `poziom = 2` i nigdy nie sprawdzono, czy inne
ustawienia trafiają częściej. W2 z fazy 1 orzekło, że `ile_kodow` nie steruje
agresywnością — ale mierzyło **dystans**, nie **odsetek trafień w bramkę**.
To dwie różne wielkości i jedna nie wynika z drugiej.

## Hipotezy

| # | hipoteza | jak obalić |
|---|---|---|
| **E07.1** | Odsetek trafień zależy od `poziom` | wszystkie trzy poziomy dają ten sam odsetek w granicach błędu |
| **E07.2** | Odsetek trafień zależy od `ile_kodow` | brak trendu wzdłuż osi `ile_kodow` |
| **E07.3** | Zwycięzcy z różnych komórek siatki są **niezależni** (nie jedna rodzina) | dystanse parami między zwycięzcami są rzędu dystansów wewnątrz jednej chmury |
| **E07.4** | Przesiew daje więcej niezależnych ziaren niż `pula_nawigator` | ≤ 3 ziarna, czyli tyle co w fazie 1 |

## Protokół

**Etap 1 — siatka.** `poziom` ∈ {0, 1, 2} × `ile_kodow` ∈ {4, 8, 12, 16, 24, 32},
`opcji` = 8 → 18 wywołań `/edycje`, 144 sekwencje. Każda przez bramkę Sędziego.
Ziarno ustalone na komórkę, więc przebieg jest powtarzalny.

**Etap 2 — niezależność.** Dla zwycięzców: macierz dystansów Hamminga parami.
Ziarna z tej samej chmury są blisko siebie; ziarna niezależne — daleko.
Zliczamy **efektywną liczbę ziaren** progiem odległości.

**Etap 3 — chmury.** Dla każdego ziarna: perturbacje o dystansie zmierzonym
w E06 (mediana dziecko↔rodzic). Bramka na każdej. Mierzymy **wydajność chmury**
— jaki odsetek potomstwa utrzymuje wygraną.

Kontrolą etapu 3 jest E06/R5: wiemy już, że ~50 % potomstwa utrzymuje wygraną.
Jeśli tutaj wyjdzie istotnie inaczej, to znaczy, że wydajność zależy od ziarna,
i to samo w sobie jest wynikiem.

## Kryterium decyzyjne

| obserwacja | konsekwencja |
|---|---|
| któraś komórka siatki trafia istotnie częściej | przesiewać tam, budżet ziaren rośnie |
| odsetek trafień płaski | przesiewać **szeroko i tanio**, parametry nieistotne |
| ≥ 10 niezależnych ziaren | portfel: wiele ziaren × mała chmura (TOP10) |
| < 5 niezależnych ziaren | przestrzeń zwycięzców jest wąska — to jest sufit tej metody i trzeba to powiedzieć |

## Zastrzeżenia

- Bramka Sędziego to **nie** miara siły promotora (W4). E07 optymalizuje
  trafianie w preferencje Sędziego, bo to jedyny sygnał, jaki mamy lokalnie.
  Że zgadza się z Wyrocznią — **zakładamy**, nie wiemy. Jedyna przesłanka jest
  taka, że pula o 39 % przejść dostała ALL100 #1.
- „Niezależność" ziaren mierzona dystansem Hamminga to niezależność
  **sekwencyjna**, nie biologiczna. Dwa odległe ziarna mogą realizować ten sam
  mechanizm.
- Przesiew jest z definicji podatny na prawo Goodharta: maksymalizujemy proxy.
  Sekcja 6 briefu wprost o tym mówi i tak trzeba to opisać przy Jury.

## Uruchomienie

```bash
python eksperymenty/E07_przesiew/run.py [--opcji 8] [--na-ziarno 8]
```

Wyjście: `wyniki.json` + `zwyciezcy.fasta` (wszystkie sekwencje przechodzące
bramkę, z atrybucją ziarna w etykiecie).
