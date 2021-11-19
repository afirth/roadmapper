.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
SHELL = /bin/bash
.SUFFIXES:

tag := roadmapper:latest
config := roadmaps.yaml

.PHONY: all
all: build run

.PHONY: build
build:
	docker build --tag $(tag) .

.PHONY: run
run:
	docker run -it --rm \
		-e GITHUB_TOKEN \
		-v ${PWD}/$(config):/app/$(config) \
		$(tag) \
		app.py --config=$(config)

.PHONY: bash
bash:
	docker run -it --rm \
		-e GITHUB_TOKEN \
		-v ${PWD}/$(config):/app/$(config) \
		$(tag) \
		--entrypoint = /bin/bash
