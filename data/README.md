# data/

Wejscia, ktorych nie commitujemy (katalog jest w `.gitignore`, poza tym plikiem):

- `dziki.fasta` — promotor wyjsciowy: `python -m hyppe dziki -o data/dziki.fasta`
- `promotory_100.csv` — 100 naturalnych promotorow Trichoderma (separator `;`),
  plik z materialow hackathonu. Wrzuccie go tutaj recznie.

Wczytanie CSV w kodzie:

```python
import csv
with open('data/promotory_100.csv', encoding='utf-8') as fh:
    ZBIOR = list(csv.DictReader(fh, delimiter=';'))
SEKWENCJE = [w['sekwencja'] for w in ZBIOR]
```

UWAGA: to nie jest zestaw dobrych odpowiedzi, tylko material porownawczy.
