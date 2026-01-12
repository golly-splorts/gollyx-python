MODULES=golly_python
VP=vp
PYTHON=$(VP)/bin/python

CB := $(shell git branch --show-current)

all:
	@echo "no default make rule defined"

help:
	cat Makefile

lint:
	$(PYTHON) -m flake8 $(MODULES)

mypy:
	$(PYTHON) -m mypy --ignore-missing-imports --no-strict-optional $(MODULES)

requirements:
	$(PYTHON) -m pip install --upgrade Cython numpy setuptools

requirements-dev:
	$(PYTHON) -m pip install --upgrade pytest flake8 mypy

build: clean
	$(PYTHON) -m pip install Cython numpy setuptools
	$(VP)/bin/cythonize -3 -i src/gollyx_python/*.pyx

test: requirements-dev build
	PYTHONPATH=src $(PYTHON) -m pytest -vs

release_mainx:
	@echo "Releasing current branch $(CB) to mainx"
	scripts/release.sh $(CB) mainx

clean:
	rm -fr build dist __pycache__ *.egg-info/