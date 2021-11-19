.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
SHELL = /bin/bash
.SUFFIXES:

tag := roadmapper:latest
config := roadmaps.yaml

.PHONY: all
all: run

.PHONY: setup
setup:
	pip install --user poetry

.PHONY: install
install:
	poetry install

.PHONY: run
run:
	poetry run python src/app.py --config $(config)
