# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComfyUI custom nodes that process dynamic prompt templates (wildcards, variants, variables, combinatorial generation) using a native lark-based parser. Implements the [sd-dynamic-prompts syntax](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/SYNTAX.md) — no dependency on the `dynamicprompts` library.

ComfyUI custom nodes are Python classes that declare their input/output types and a processing function. They are auto-discovered by ComfyUI at startup via `NODE_CLASS_MAPPINGS` exported from the package.

## Commands

```bash
# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run a single test
pytest tests/path/to/test_file.py::test_name

# Lint
ruff check .
ruff format .

# Type check
mypy

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

### Native Parser & Evaluator

Templates are processed by a native lark PEG grammar pipeline:

```
src/
  parser/
    grammar.lark         # PEG grammar for the full sd-dynamic-prompts syntax
    ast_nodes.py         # dataclasses for every AST node type
    parser.py            # lark Transformer → AST
  evaluator/
    context.py           # EvaluationContext (rng, wildcard_manager, variables, counters)
    random_eval.py       # random sampling evaluator
    combinatorial_eval.py  # exhaustive cross-product evaluator
    cyclical_eval.py     # cyclical (ordered) evaluator
  wildcards.py           # native WildcardManager — loads .txt/.yaml/.json files
  nodes/
    random_prompt.py     # DynamicPromptRandom node
    combinatorial_prompt.py
    cyclical_prompt.py
```

**AST node types:** `Text`, `Template`, `Variant`, `Wildcard`, `Variable`, `WeightedOption`

**EvaluationContext** holds all mutable state: `rng`, `wildcard_manager` (Protocol), `variables`, `resolved`, `cycle_counters`.

**WildcardManager** (`src/wildcards.py`): loads `.txt`, `.yaml`, and `.json` files from one or more directories. Wildcard names for `.txt` files are the relative file path without extension. For `.yaml`/`.json`, nested dict keys are joined with `/` as the wildcard name. Pattern matching uses `fnmatch`.

Wildcard files live in `wildcards/` and can be `.txt` (one value per line) or `.yaml` (nested keys referenced with `/`).

### Code Style

- Line length: 140
- Indent: 4 spaces
- Quotes: double (`"`)
- mypy strict mode — all production code must be fully typed; test files are exempt
- `exec` and `eval` are banned (ruff rules S102/S307)
