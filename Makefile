VENV_NAME ?= venv
PYTHON = python3

.PHONY: venv clean run

default: venv download run

venv:
	$(PYTHON) -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install --upgrade pip
	$(VENV_NAME)/bin/pip install -r requirements.txt

download: # Try to get official image
	$(VENV_NAME)/bin/python download.py

crawl:  # Grab first image search result
	env PGV_CRAWL=1 $(VENV_NAME)/bin/python download.py

fill:   # Fill any missing results
	env PGV_FILL=1 $(VENV_NAME)/bin/python download.py

run:
	$(VENV_NAME)/bin/python app.py

clean:
	rm -rf $(VENV_NAME) __pycache__ *.pyc
