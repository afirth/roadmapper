.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
SHELL = /bin/bash
.SUFFIXES:

tag := roadmapper:latest

.PHONY: all
all: build run

.PHONY: build
build:
	docker build --tag $(tag) .

.PHONY: run
run:
	docker run -it --rm \
		-e GITHUB_TOKEN \
		$(tag) \
		app.py --owner=FATMAP --repo=aws-dns-zones
