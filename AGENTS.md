# AGENTS.md

## Setup
- Python >=3.10 required
- Install all dependencies (including dev): `pip install -e ".[dev]"`

## Commands
- Lint: `make lint` (ruff)
- Format: `make format` (ruff)
- Typecheck: `make typecheck` (mypy on `src/`)
- Run all tests: `make test` (pytest)
- Run single test: `pytest tests/test_file.py::test_name`
- CI runs in order: lint → typecheck → test

## Architecture
- Main package: `src/fluidlearn/`
- Tests: `tests/` (pytest, shared fixtures in `conftest.py`)

## Config
- Ruff/mypy config: `pyproject.toml`
- Dev dependencies: `pyproject.toml` `[project.optional-dependencies]`
