# Hack the Promoter — repo zespołu

Klient API + CLI + przestrzeń na rozwijanie rozwiązania do hackathonu
**iGEM Warsaw 2026 „Hack the Promoter"** (projektowanie silnego promotora `pks1`
w *Trichoderma atroviride* P1).

Zero zależności zewnętrznych — działa na gołym Pythonie ≥ 3.10 (tylko stdlib).
`pandas`/`matplotlib` są opcjonalne, wyłącznie do analiz.

---

## Start w 60 sekund

```bash
git clone <adres-repo> && cd hack-the-promoter
cp .env.example .env          # wklej swój klucz do HYPPE_API_KEY
make test                     # 65 testów offline, bez sieci i bez klucza
make smoke                    # sprawdza, czy API i klucz działają
python -m hyppe dziki -o data/dziki.fasta
```

Opcjonalnie `pip install -e .` — wtedy zamiast `python -m hyppe` piszesz `hyppe`.

### Konfiguracja

Wszystko idzie przez `.env` (jest w `.gitignore`, **nie commitujemy kluczy**):

| zmienna | domyślnie | opis |
|---|---|---|
| `HYPPE_API_KEY` | — | indywidualny klucz, nagłówek `X-API-Key` |
| `HYPPE_URL` | `https://hyppe.futura.foundation` | adres API |
| `HYPPE_TIMEOUT` | `900` | timeout requestu (s) |
| `HYPPE_RETRIES` | `6` | próby przy 429/503 |
| `HYPPE_USER_AGENT` | przeglądarkowy | bez UA Cloudflare zwraca `error code: 1010` |

Zmienna ze środowiska wygrywa z `.env`, a flaga `--api-key` z obiema — wygodne,
gdy testujesz drugi klucz: `python -m hyppe --api-key XXX me`.

---

## CLI

Każda komenda przyjmuje globalne `--api-key`, `--url`, `--json`
(`--json` = surowa odpowiedź serwera, dobra do `jq` i do debugowania).

Gdziekolwiek komenda przyjmuje sekwencję, można podać: `dziki` (pobierze z API),
**ścieżkę do pliku** (FASTA albo goły tekst) albo **wklejoną sekwencję**.

| komenda | co robi |
|---|---|
| `me` | stan klucza, limity, ile sekund do następnego wgrania |
| `dziki [-o plik]` | promotor wyjściowy 800 pz + GC i suma kontrolna |
| `mapa [seq] [--zastosuj plik]` | mapa Nawigatora: rekomendacje, pozycje swobodne, nadpisywane |
| `edycje [seq] [--poziom 0/1/2] [-o plik]` | warianty z edycji latentu |
| `sedzia A B` / `sedzia --plik F.fasta` | pojedynczy pojedynek albo cały plik vs baza |
| `pula --strategia X [--ile 100]` | generuje pulę kandydatów i zapisuje FASTA |
| `waliduj F.fasta [--fix out.fasta]` | filtry serwera **lokalnie**, przed wysyłką |
| `wgraj F.fasta [-n] [--force]` | zgłoszenie (raz na 5 min) |
| `ranking` | tablica wyników |
| `analiza [seq] [--porównaj inna]` | offline: GC, skład, motywy, diff pozycji |

### Typowa sesja

```bash
# 1. co Nawigator mówi o dzikim i od razu wariant z naniesionymi radami
python -m hyppe mapa dziki --zastosuj runs/julian/z_mapy.fasta

# 2. pula 100 kandydatów jedną ze strategii
python -m hyppe pula --strategia hybryda --ile 100 -o runs/julian/pula.fasta

# 3. które przebijają dzikiego (Sędzia), zwycięzcy do osobnego pliku
python -m hyppe sedzia --plik runs/julian/pula.fasta --baza dziki \
                       -o runs/julian/wygrane.fasta

# 4. walidacja lokalna — ZANIM zużyjesz okno 5 minut
python -m hyppe waliduj runs/julian/pula.fasta

# 5. próba na sucho, potem wysyłka
python -m hyppe wgraj runs/julian/pula.fasta --dry-run
python -m hyppe wgraj runs/julian/pula.fasta
python -m hyppe ranking
```

### Zabezpieczenia, które celowo są w CLI

- `wgraj` **odmawia** wysłania mniej niż 100 sekwencji bez `--force` — dzielnik
  ALL100 jest stały, więc 50 sekwencji to z definicji połowa punktów w tej kategorii.
- `wgraj` i `waliduj` odtwarzają filtry serwera lokalnie (800 pz, `ACGTN`,
  ≤ 10 % `N`, unikalność) — nie marnujemy okna 5 minut na plik, który i tak odpadnie.
- Klient sam pilnuje limitów na minutę (570/min dla Sędziego i Nawigatora,
  228/min dla reszty POST) i ponawia 503 oraz 429 — **poza `/wgraj`**, gdzie 429
  znaczy „czekaj 5 minut", więc ponawianie tylko by szkodziło.
- Odpowiedź `/wgraj` ląduje w `runs/ostatnie_wgranie.json`.

---

## Użycie z kodu (automatyzacja)

Wszystko, co robi CLI, jest dostępne jako biblioteka — CLI to cienka warstwa nad `hyppe.Client`.

```python
from hyppe import Client
from hyppe import fasta as F

c = Client.from_env()                    # czyta .env
dziki = c.dziki_seq()

m = c.mapa(dziki)                        # mapa pozycji
kandydat = c.zastosuj_rekomendacje(dziki, m)

if c.lepsza(dziki, kandydat):            # bool zamiast grzebania w JSON-ie
    print("kandydat wygrywa")

e = c.edycje(dziki, poziom=2, ile_kodow=8, opcji=8, ziarno=1)
pula = {f"edy_{o['nr']}": o["sekwencja"] for o in e["opcje"]}

wygrane = c.turniej(dziki, pula)                 # kto przebija bazę
kolejnosc = c.ranking_swiss(pula, rund=5)        # ranking bez każdy-z-każdym

raport = F.waliduj([F.Rekord(n, s) for n, s in pula.items()])
c.wgraj(F.na_tekst(raport.ok[:100]))
```

Pełny przebieg (dziki → pula → selekcja → FASTA → wgraj) jest w
`scripts/przyklad_workflow.py`:

```bash
python scripts/przyklad_workflow.py --strategia hybryda --ile 100 --kto julian
python scripts/przyklad_workflow.py --strategia hybryda --wgraj
```

### Warstwy repo

```
hyppe/
  config.py      .env, ustawienia            <- rzadko dotykane
  client.py      HTTP, retry, rate-limit, helpery Sędzia/Nawigator
  fasta.py       czytanie/zapis/walidacja FASTA (filtry serwera)
  seq.py         mutacje, crossover, GC, motywy IUPAC  <- czysto offline
  strategie/     TU PISZEMY POMYSŁY (jeden plik = jedna osoba)
  cli.py         cienka warstwa nad powyższym
scripts/         smoke.py, przyklad_workflow.py
tests/           65 testów offline
data/            wejścia (dziki, promotory_100.csv) — gitignore
runs/            wyniki: runs/<imię>/... — gitignore
```

---

## Jak sobie nie wchodzić w drogę

**1. Strategie w osobnych plikach.** Katalog `hyppe/strategie/` jest
auto-importowany, więc każdy zakłada **własny plik** i nikt nie rusza cudzego —
zero konfliktów w gicie. Nowa strategia = funkcja z dekoratorem:

```python
# hyppe/strategie/julian.py
from . import strategia

@strategia("julian-tata")           # nazwa musi być unikalna w zespole
def moja(c, baza, ile=100, **_):
    """Wstawia kanoniczny TATA-box w oknie -80..-30 i mutuje resztę."""
    from ..seq import mutuj, wstaw
    out = {}
    for i, poz in enumerate(range(720, 770)):
        out[f"tata_{poz}"] = mutuj(wstaw(baza, "TATAAA", poz), ile=5, ziarno=i)
    return out                       # {etykieta: sekwencja}
```

Od razu działa w CLI: `python -m hyppe pula --strategia julian-tata`.
Prefiksujcie nazwy swoim imieniem — etykieta trafia do nagłówka FASTA, więc po
zgłoszeniu widać, czyj pomysł co dał.

**2. Wyniki w `runs/<imię>/`.** Nikt nikomu nie nadpisuje plików;
`runs/` i `data/` są w `.gitignore`, więc do repo trafia kod, nie artefakty.

**3. Jedno okno 5 minut na klucz — uzgadniajcie wysyłki.** Liczy się
**najlepszy** wynik drużyny, nie ostatni, więc słabsze zgłoszenie niczego nie
psuje; kosztuje tylko okno. Przed każdym `wgraj` sprawdź `python -m hyppe me`
(pole `zgloszenie_mozliwe_za_s`) i najpierw `--dry-run`.

**4. Git.** Gałąź na osobę/pomysł (`julian/tata-box`), `main` zostaje zielony:
`make test` przed każdym pushem.

---

## Testy

```bash
make test                                   # albo: python -m unittest discover -s tests -t .
python -m unittest tests.test_fasta -v      # pojedynczy moduł
pytest                                      # też działa, jeśli macie pytest
```

Testy są **offline** — nie ruszają sieci i nie potrzebują klucza (transport jest
zamockowany), więc można je odpalać bez limitu. Pokrywają m.in.:

- **próg `N`**: 80 `N` (= dokładnie 10 %) przechodzi, 81 odpada — łącznie z małymi literami,
- długość ≠ 800, znaki spoza `ACGTN`, duplikaty (zostaje pierwsze wystąpienie),
- ostrzeżenie i twardy stop przy < 100 sekwencji,
- niezmiennik 800 pz po `mutuj`/`krzyzuj`/`wstaw` (żeby strategia nie wyprodukowała śmieci),
- retry: 503 i 429 ponawiane, 429 na `/wgraj` **nie**, 422 nie,
- rate-limiter, parser FASTA łamany na wiele linii, komendy CLI.

### Smoke test API

`make test` nie dotyka sieci — do sprawdzenia, czy API żyje i czy klucz działa,
służy osobny skrypt:

```bash
python scripts/smoke.py            # /me, /dziki, /nawigator/mapa, /nawigator/edycje, /sedzia, /ranking
python scripts/smoke.py --wgraj    # dodatkowo próbne zgłoszenie — ZUŻYWA okno 5 minut
```

Wypisuje OK/FAIL i czas każdego endpointu, kod wyjścia 0/1 (nadaje się do CI).
`/wgraj` jest domyślnie pomijane i samo się pomija, gdy okno jeszcze trwa.

---

## Ściąga: reguły zadania

- sekwencja: **dokładnie 800 pz**, znaki `ACGTN`, **≤ 10 % `N`**, unikalna w pliku;
- oceniane jest **pierwsze 100** sekwencji po filtrach, nadmiar leci do kosza;
- TOP10 i ALL100 mają **stałe dzielniki** (10 i 100) → zawsze wysyłamy pełne 100;
- punktacja rangowa, liczy się **najlepszy** wynik, remis rozstrzyga wcześniejsza data;
- Sędzia i Nawigator nie znają kontekstu genu, Wyrocznia (niedostępna) ocenia w kontekście `pks1`;
- kody błędów: 401 brak klucza, 403 zły klucz, 422 zła sekwencja, 429 limit, 503 kolejka GPU.

Model nie był walidowany laboratoryjnie — wynik to predykcja modelu, nie aktywność mokra.
