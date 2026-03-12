# Design: Decouple from dynamicprompts — Native Parser & Evaluator

**Date:** 2026-03-12

## Context

The `dynamicprompts` library does not support variables (`${name=value}`), which is a required feature. We replace its parser and generators with a native implementation targeting full syntax parity with [sd-dynamic-prompts SYNTAX.md](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/SYNTAX.md).

`dynamicprompts.WildcardManager` is kept for wildcard file I/O (`.txt`, `.yaml`, `.json`) and removed from everywhere else.

The Jinja node (`DynamicPromptJinja`) is dropped.

---

## Syntax Coverage

Full parity with the sd-dynamic-prompts spec:

- **Variants** — `{a|b}`, weighted `{0.5::a|b}`, multi-pick `{2$$a|b}`, custom separator `{2$$ and $$a|b}`, range `{1-2$$a|b}`
- **Wildcards** — `__name__`, glob `__colours*__`, recursive `__artists/**__`, sampler prefix `__~name__` / `__@name__`
- **Variables** — `${name=value}` (non-immediate), `${name=!value}` (immediate), `${name:default}`, `${name}`
- **Parameterized templates** — `__name(var=val)__`
- **Whitespace & comments** — ignored whitespace around structural tokens, `#` line comments
- **Samplers** — random (default), combinatorial, cyclical (`@`)

---

## Architecture

### Source Layout

```
src/
  parser/
    grammar.lark         # lark PEG grammar
    ast_nodes.py         # dataclasses for every AST node type
    parser.py            # lark Transformer → AST
  evaluator/
    context.py           # EvaluationContext: rng, variables, cycle counters
    random_eval.py       # random mode
    combinatorial_eval.py
    cyclical_eval.py
  wildcards.py           # unchanged — wraps dynamicprompts.WildcardManager
  nodes/
    __init__.py
    random_prompt.py
    combinatorial_prompt.py
    cyclical_prompt.py   # new
tests/
  parser/
    test_parser.py
  evaluator/
    test_random_eval.py
    test_combinatorial_eval.py
    test_cyclical_eval.py
  test_wildcards.py
  test_nodes.py
```

---

## Grammar & AST

The lark grammar is a PEG grammar. Whitespace around structural tokens (`{`, `}`, `|`, `$$`, `__`) is ignored; whitespace within text tokens is preserved. `#` comments consume to end of line and are discarded at parse time. Sampler prefixes (`~`, `@`) are optional on variants and wildcards.

### AST Node Types

```python
@dataclass
class Text:
    value: str

@dataclass
class Template:
    parts: list[Node]               # top-level sequence

@dataclass
class WeightedOption:
    weight: float                   # default 1.0
    node: Node

@dataclass
class Variant:
    min_count: int                  # default 1
    max_count: int                  # default 1
    separator: str                  # default ", "
    sampler: Literal["random", "combinatorial", "cyclical"]
    options: list[WeightedOption]

@dataclass
class Wildcard:
    pattern: str                    # e.g. "season", "colours*", "artists/**"
    sampler: Literal["random", "combinatorial", "cyclical"]
    params: dict[str, str]          # for __name(var=val)__

@dataclass
class Variable:
    name: str
    value: Node | None              # None = read-only reference
    immediate: bool                 # True when ${name=!...}
    default: str | None             # for ${name:default}
```

---

## EvaluationContext

Holds all mutable state for one evaluation run:

```python
@dataclass
class EvaluationContext:
    rng: random.Random
    wildcard_manager: WildcardManager
    variables: dict[str, Node]      # name → AST node (non-immediate)
    resolved: dict[str, str]        # name → string (immediate, already evaluated)
    cycle_counters: dict[str, int]  # key → int (cyclical sampler state)
```

Variable lookup order: `resolved` → `variables` (re-evaluate) → `default` → error.

---

## Evaluators

Each evaluator exposes a single entry point: `evaluate(node: Node, ctx: EvaluationContext) -> list[str]`.

| Evaluator | Returns | Behaviour |
|---|---|---|
| `random_eval` | `["one result"]` | samples randomly; inline `{@...}` uses `ctx.cycle_counters` |
| `combinatorial_eval` | `["all", "combinations"]` | cross-product of all options; variables evaluated once per branch |
| `cyclical_eval` | `["one result"]` | all variants and wildcards use `ctx.cycle_counters`; advances counters after each call |

**Cycle counter key format:** `f"{node_instance_id}:{template_hash}:{ast_position}"` — stable per node instance, resets only when the template changes.

---

## Nodes

| Node | Inputs | Outputs | Evaluator |
|---|---|---|---|
| `DynamicPromptRandom` | template, seed | prompt | `random_eval` |
| `DynamicPromptCombinatorial` | template, index | prompt, all_prompts, total_count | `combinatorial_eval` |
| `DynamicPromptCyclical` | template | prompt | `cyclical_eval` |

`DynamicPromptCyclical` stores `cycle_counters` on `self` (persists across ComfyUI calls), returns `float("nan")` from `IS_CHANGED` so ComfyUI re-executes it every generation.

`DynamicPromptRandom` uses fresh counters per call — inline `{@...}` syncs values within one prompt but does not persist state across runs.

---

## Testing Strategy

```
tests/
  parser/test_parser.py          # grammar round-trips: parse → AST shape
  evaluator/test_random_eval.py  # variants, wildcards, variables, weights
  evaluator/test_combinatorial_eval.py
  evaluator/test_cyclical_eval.py
  test_wildcards.py              # unchanged
  test_nodes.py                  # smoke: nodes instantiate and generate output
```

**Key test cases:**
- Variable immediate: `${x=!{a|b}} ${x} ${x}` → both uses identical within one call
- Variable non-immediate: `${x={a|b}} ${x} ${x}` → uses may differ
- Nested constructs parse and evaluate correctly
- Combinatorial cross-product: `{a|b} {c|d}` → exactly 4 results
- Cyclical counter advances across node calls on the same instance
- Wildcard globbing: `__colours*__` resolves values from both fixture files
- Parameterized template: `__tmpl(season=winter)__` substitutes correctly
- Weighted sampling: weighted options sampled proportionally (large N)
- Comments stripped: `# comment\n{a|b}` parses identically to `{a|b}`

---

## Dependencies

| Package | Role | Change |
|---|---|---|
| `lark` | PEG parser | **add** |
| `dynamicprompts` | WildcardManager file I/O only | keep, scope reduced |
| `pyyaml` | already transitive | no change |
