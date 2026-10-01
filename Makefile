SHELL := /bin/bash
.PHONY: doctor build lint typecheck

doctor:
	uv run --python 3.12 python scripts/doctor.py

build:
	uv sync --frozen --all-packages --group dev
	pnpm --dir apps/web install --frozen-lockfile
	pnpm --dir apps/web build
	docker pull python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
	docker pull node:24-bookworm-slim@sha256:2fe369e969550cde8e867afc3fe370b260140cab4a23d467074295b42163d553
	docker build -f apps/api/Dockerfile -t ai-dspm-api:dev .
	docker build -f apps/web/Dockerfile -t ai-dspm-web:dev .

lint:
	uv run --python 3.12 ruff check apps packages workers scripts tests
	pnpm --dir apps/web exec tsc -b --pretty false

typecheck:
	uv run --python 3.12 mypy


CHECK ?=
PHASE ?=

verify:
	@if [ -z "$(CHECK)" ]; then echo "usage: make verify CHECK=product-contract"; exit 1; fi
	uv run --python 3.12 python scripts/verify.py --check $(CHECK)

gate:
	@if [ -z "$(PHASE)" ]; then echo "usage: make gate PHASE=foundations"; exit 1; fi
	uv run --python 3.12 python scripts/verify.py --gate-phase $(PHASE)

evidence:
	@if [ -z "$(CHECK)" ]; then echo "usage: make evidence CHECK=verify-harness"; exit 1; fi
	uv run --python 3.12 python scripts/verify.py --check $(CHECK)