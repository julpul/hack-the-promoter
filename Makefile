.PHONY: test smoke smoke-full me ranking dziki lint clean

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
