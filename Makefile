.PHONY: test smoke smoke-full me ranking dziki lint clean \
        e-test e01 e02 e03 e04 e-portfel e-notebook e-wszystko

PY ?= python3

test:            ## testy offline (bez sieci, bez klucza)
	$(PY) -m unittest discover -s tests -t . -v

smoke:           ## sprawdz endpointy API (bez /wgraj)
	$(PY) scripts/smoke.py

smoke-full:      ## jw. + probne /wgraj (blokuje okno 5 min!)
	$(PY) scripts/smoke.py --wgraj

me:
	$(PY) -m hyppe me

ranking:
	$(PY) -m hyppe ranking

dziki:
	$(PY) -m hyppe dziki -o data/dziki.fasta

clean:
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

notebook:        ## przebuduj i wykonaj hipotezy.ipynb
	.venv/bin/python scripts/zbuduj_notebook.py
	.venv/bin/jupyter nbconvert --to notebook --execute --inplace hipotezy.ipynb --ExecutePreprocessor.timeout=600
	.venv/bin/jupyter nbconvert --to html hipotezy.ipynb --output hipotezy.html

pomiary:         ## odswiez data/pomiary.json z API
	.venv/bin/python scripts/zbierz_pomiary.py

venv:            ## srodowisko do notebooka
	python3 -m venv .venv && .venv/bin/pip install -q seaborn pandas matplotlib jupyter nbconvert ipykernel

# ── eksperymenty fazy 2 (patrz eksperymenty/README.md) ──────────────────────

e-test:          ## caly lancuch E01-E05 na zamockowanym API, bez sieci
	$(PY) eksperymenty/test_offline.py

e01:             ## funkcja celu z naglowka /mapa   [BLOKUJACY, ~2 min]
	$(PY) eksperymenty/E01_funkcja_celu/run.py

e02:             ## kontrola artefaktu wagaP        [BLOKUJACY, ~1 min]
	$(PY) eksperymenty/E02_artefakt_wagap/run.py

e03:             ## naturalne promotory Trichoderma  [wymaga data/promotory_100.csv]
	$(PY) eksperymenty/E03_naturalne_promotory/run.py

e04:             ## plan faktorialny 2^4
	$(PY) eksperymenty/E04_blok_kombinacyjny/run.py

e-portfel:       ## zbuduj 100 sekwencji -> runs/julian/v2.fasta
	$(PY) eksperymenty/E05_portfel/portfel.py -o runs/julian/v2.fasta

e-notebook:      ## przebuduj i wykonaj eksperymenty/eksperymenty.ipynb
	.venv/bin/python eksperymenty/zbuduj_notebook.py
	.venv/bin/jupyter nbconvert --to notebook --execute --inplace \
		eksperymenty/eksperymenty.ipynb --ExecutePreprocessor.timeout=600

e-wszystko: e01 e02 e03 e04 e-portfel e-notebook   ## cala faza 2 po kolei
