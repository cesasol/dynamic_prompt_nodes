# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComfyUI custom nodes that process dynamic prompt templates (wildcards, variants, combinatorial generation) using the [dynamicprompts](https://github.com/adieyal/dynamicprompts) library. Targets feature parity with [sd-dynamic-prompts](https://github.com/adieyal/sd-dynamic-prompts).

ComfyUI custom nodes are Python classes that declare their input/output types and a processing function. They are auto-discovered by ComfyUI at startup via `NODE_CLASS_MAPPINGS` exported from the package.

## Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run a single test
pytest tests/path/to/test_file.py::test_name

# Lint
ruff check .
ruff format .

# Type check
mypy .

# Install pre-commit hooks
pre-commit install
```

Package manager is `uv` (lockfile: `uv.lock`). Use `uv pip install` instead of `pip install` when managing the venv at `.venv/`.

## Architecture

### ComfyUI Node Registration

Every ComfyUI custom node package must export from its top-level `__init__.py`:
- `NODE_CLASS_MAPPINGS` — dict mapping node type name → class
- `NODE_DISPLAY_NAME_MAPPINGS` — dict mapping node type name → human-readable label

Each node class needs:
- `INPUT_TYPES` — classmethod returning input schema
- `RETURN_TYPES` — tuple of output type strings (e.g. `("STRING",)`)
- `FUNCTION` — name of the method to call
- `CATEGORY` — node browser category string

### dynamicprompts Integration

The core processing delegates entirely to `dynamicprompts`. Key classes:
- `RandomPromptGenerator` — random sampling from templates
- `CombinatorialPromptGenerator` — exhaustive enumeration of all combinations
- `JinjaGenerator` — Jinja2 template processing
- `WildcardManager` — resolves `__wildcard__` tokens from files in `wildcards/`

Wildcard files live in `wildcards/` and can be `.txt` (one value per line) or `.yaml` (nested keys referenced with `/`).

### Code Style

- Line length: 140
- Indent: 4 spaces
- Quotes: double (`"`)
- mypy strict mode — all production code must be fully typed; test files are exempt
- `exec` and `eval` are banned (ruff rules S102/S307)
