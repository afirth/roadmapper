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
		-v ${PWD}/roadmaps.yaml:/app/roadmaps.yaml \
		$(tag) \
		app.py --owner=FATMAP --repo=aws-dns-zones

.PHONY: bash
bash:
	docker run -it --rm \
		-e GITHUB_TOKEN \
		-v ${PWD}/roadmaps.yaml:/app/roadmaps.yaml \
		$(tag) \
		--entrypoint = /bin/bash
