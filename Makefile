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
