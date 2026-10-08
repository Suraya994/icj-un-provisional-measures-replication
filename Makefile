.PHONY: all reproduce check test manifest
all: reproduce check test
reproduce:
	python3 code/reproduce_published_results.py
	python3 code/reproduce_additional_results.py
check:
	python3 code/check_paper_concordance.py
	python3 code/validate_release.py
test:
	python3 -m unittest discover -s tests -v
manifest:
	python3 code/make_manifest.py
