.PHONY: install test analysis refresh notebook

install:
	pip install -e . -r requirements.txt

test:
	pytest -q

analysis:
	python scripts/run_analysis.py

refresh:
	python scripts/run_analysis.py --refresh

notebook:
	jupyter nbconvert --to notebook --execute notebooks/analysis.ipynb --output analysis.ipynb --output-dir notebooks --ExecutePreprocessor.timeout=180
