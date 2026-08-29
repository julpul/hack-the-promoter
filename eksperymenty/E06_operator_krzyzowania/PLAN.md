# E06 · Operator krzyżowania — rekombinacja czy dziedziczenie?

**Status:** [OTWARTE] · **Blokuje:** E05 · **Koszt:** ~350 wywołań, 3 min

---

## Obserwacja, która to wywołała

Rozbicie wgranej puli (`runs/julian/pula.fasta`, 100 sekwencji) na sposób
powstania — pomiar z E01, 92 sekwencje z werdyktem Sędziego:

| prefiks | jak powstała | bije dzikiego |
|---|---|---|
| `nav_*` | surowe wyjście `/nawigator/edycje` | **3 / 49 (6 %)** |
| `hyb_*` | krzyżówka dwóch zwycięzców + 0–6 mutacji | **36 / 50 (72 %)** |
| `z_mapy` | dziki + rekomendacje gatunkowe | 0 / 1 |

Dwunastokrotna różnica. Dla porównania E04, gdzie tłem D=1 było surowe
wyjście dekodera (`ile_kodow=8`): **0 / 24**, czyli zgodnie z `nav_*`.

**Krzyżowanie jest najsilniejszym operatorem, jaki mamy** — i nie występuje
w żadnym planie jako hipoteza. W fazie 1 było linijką w środku strategii
`hybryda`, obok właściwego pomysłu. Cała reszta projektu optymalizowała rzeczy,
które w tej tabeli nie robią nic.

## Dlaczego nie wolno tego wziąć wprost do portfela

`pula_hybryda` krzyżuje **zwycięzców turnieju** (`c.turniej(baza, nav)`), a nie
losowe sekwencje. Skoro `nav_*` wygrywa 6 % razy, rodziców było około trzech —
i wszystkie 50 krzyżówek pochodzi z tej garstki. Efekt operatora jest więc
pomieszany z **preselekcją rodziców**. Dwa wyjaśnienia pasują do tych samych liczb:

- **operator** — rekombinacja dwóch wyjść dekodera trafia w rejon, którego sam
  dekoder nie generuje, niezależnie od jakości rodziców;
- **dziedziczenie** — dzieci wygrywają, bo rodzice wygrywali, a krzyżowanie
  tylko nie psuje.

Rozstrzyga jedno ramię: **krzyżowanie dwóch PRZEGRANYCH**. Jeśli ich dzieci
wygrywają — działa operator. Jeśli nie — działała selekcja, a wtedy portfel
powinien wyglądać zupełnie inaczej.

To jest dokładnie reguła 1 z `README.md` („kontrola negatywna albo nie ma
wniosku") zastosowana do wyniku, który inaczej wprost sterowałby zgłoszeniem.

## Hipotezy

| # | hipoteza | jak obalić |
|---|---|---|
| **E06.1** | Krzyżowanie podnosi odsetek wygranych **niezależnie od jakości rodziców** | R2 (dzieci przegranych) wygrywa nie częściej niż R1 (surowy dekoder) |
| **E06.2** | Efekt to rekombinacja, nie samo oddalenie się od rodzica | R5 (mutacja o ten sam dystans) wygrywa tak samo często jak R3 |
| **E06.3** | Dziecko bije **własnych rodziców**, nie tylko dzikiego | dzieci nigdy nie biją rodziców — wtedy to dziedziczenie |
| **E06.4** | Efekt kumuluje się przez pokolenia | R6 (drugie pokolenie) nie jest lepsze od R3 |

## Ramiona

Wszystkie po 16 sekwencji, wspólny zbiór rodziców z jednego zaciągu `/edycje`.

| # | ramię | co mierzy |
|---|---|---|
| R1 | surowe `/edycje` | **kontrola bazowa** — oczekiwane ~6 % |
| R2 | krzyżówka dwóch **przegranych** | **ramię rozstrzygające** (E06.1) |
| R3 | krzyżówka dwóch **zwycięzców** | replikacja `hybryda` |
| R4 | zwycięzca × **dziki** | czy drugi rodzic musi być z dekodera |
| R5 | zwycięzca + losowe podstawienia o **tym samym dystansie** co R3 | **kontrola dystansu** (E06.2) |
| R6 | krzyżówka dzieci z R3 (**drugie pokolenie**) | czy efekt się kumuluje (E06.4) |

R5 jest kontrolą, bez której E06.2 nie da się rozstrzygnąć: dziecko krzyżówki
leży średnio w połowie drogi między rodzicami, więc **jest oddalone** od każdego
z nich. Trzeba pokazać, że liczy się skąd wzięte są litery, a nie ile ich się
zmieniło. Liczba podstawień w R5 jest brana z **faktycznie zmierzonej** mediany
dystansu dziecko↔rodzic w R3, a nie zgadywana.

## Pomiar

Dla każdej sekwencji: `lepsza(dziki, x)`, `lepsza(rodzic_a, x)`,
`lepsza(rodzic_b, x)`, `mapa(x)` → metryki, dystanse do dzikiego i do obu rodziców.

Porównanie z rodzicami jest tu ważniejsze niż z dzikim: odpowiada na E06.3,
czyli czy rekombinacja **tworzy** coś lepszego, czy tylko **przenosi** wygraną.

## Kryteria decyzyjne

| obserwacja | wniosek | konsekwencja dla E05 |
|---|---|---|
| R2 ≈ R3 >> R1 | działa **operator** | portfel budować krzyżowaniem, rodzice nieistotni — maksimum różnorodności |
| R3 >> R2 ≈ R1 | działa **selekcja** | najpierw wyłonić zwycięzców, dopiero potem krzyżować; portfel węższy |
| R5 ≈ R3 | to nie rekombinacja, tylko dystans | wrócić do mutacji, operator nieistotny |
| dzieci nie biją rodziców | **dziedziczenie** | krzyżowanie nie poprawia, tylko nie psuje |
| R6 > R3 | efekt kumulatywny | wprowadzić kilka pokoleń przed zgłoszeniem |

## Zastrzeżenia

- Sędzia jest bramką, nie miarą siły (W4). „Bije dzikiego" znaczy „Nawigator
  uznaje to za bardziej prototypowy promotor", nie „silniejszy promotor".
  E06 mierzy więc, jak trafiać w preferencje Sędziego — nie jak zwiększyć ekspresję.
- Sędzia jest **powtarzalny** (E01: 8/8 albo 0/8 na siedmiu parach), więc
  odsetki wygranych nie są szumem pomiarowym. To jedyny powód, dla którego
  różnicę 6 % vs 72 % wolno w ogóle interpretować.
- 16 sekwencji na ramię daje przedział ±~12 pp. Różnice poniżej 20 pp między
  ramionami należy traktować jako nierozstrzygnięte.

## Uruchomienie

```bash
python eksperymenty/E06_operator_krzyzowania/run.py [--na-ramie 16]
```
