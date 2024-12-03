SHELL := /bin/bash

#######################################################################
# Setup of development environment
#######################################################################

.PHONY: dev
dev:
	python3.12 -m venv .venv --upgrade-deps
	source .venv/bin/activate && pip3 install -r requirements.txt

.PHONY: fix-format
fix-format:
	.venv/bin/ruff format .
	.venv/bin/ruff check . --fix --fixable I
