# Dynamic Prompt Nodes

ComfyUI custom nodes for dynamic prompt generation with full wildcard and variable support. Implements the [sd-dynamic-prompts syntax](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/SYNTAX.md) natively — no external generator dependency.

## Features

- **Random sampling** — pick random variants from `{option1|option2|option3}`
- **Combinatorial generation** — enumerate every possible prompt combination
- **Cyclical sampling** — cycle through options in order across generations
- **Wildcards** — substitute values from `.txt` or `.yaml` wildcard files using `__wildcard_name__`
- **Variables** — define and reuse values within a prompt via `${name=value}`

## Installation

### Via ComfyUI Manager
Search for **Dynamic Prompt Nodes** and install.

### Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cesasol/dynamic_prompt_nodes
cd dynamic_prompt_nodes
pip install -e .
```

Place wildcard files (`.txt` or `.yaml`) in `ComfyUI/custom_nodes/dynamic_prompt_nodes/wildcards/`.

## Nodes

### Dynamic Prompt (Random)
Processes a prompt template and returns a randomly sampled string each generation.

**Inputs:** `template` (STRING), `seed` (INT)
**Output:** `prompt` (STRING)

### Dynamic Prompt (Combinatorial)
Enumerates all combinations from a template. Feed into a batch to generate every variant.

**Inputs:** `template` (STRING), `index` (INT)
**Outputs:** `prompt` (STRING), `all_prompts` (STRING), `total_count` (INT)

### Dynamic Prompt (Cyclical)
Steps through options in order, advancing one position each generation. Useful for systematic variation without randomness.

**Inputs:** `template` (STRING)
**Output:** `prompt` (STRING)

## Syntax

### Variants

| Syntax | Description |
|--------|-------------|
| `{cat\|dog\|bird}` | Pick one randomly |
| `{2$$cat\|dog\|bird}` | Pick exactly 2 |
| `{1-3$$cat\|dog\|bird}` | Pick 1 to 3 |
| `{2$$ and $$cat\|dog}` | Pick 2 with custom separator |
| `{3::rare\|1::common}` | Weighted selection |
| `{@cat\|dog\|bird}` | Cyclical (steps each call) |

### Wildcards

| Syntax | Description |
|--------|-------------|
| `__animals__` | Substitute from `wildcards/animals.txt` |
| `__colors/warm__` | Nested key or subdirectory |
| `__colors*__` | Glob match wildcard names |
| `__~animals__` | Random sampler (explicit) |
| `__@animals__` | Cyclical sampler |

### Variables

| Syntax | Description |
|--------|-------------|
| `${x=value}` | Assign (non-immediate — re-evaluated each use) |
| `${x=!value}` | Assign immediate — fixed once, same value every use |
| `${x}` | Read variable |
| `${x:fallback}` | Read with default |

### Wildcard Files

**Text format** (`wildcards/animals.txt`):
```
cat
dog
bird
# lines starting with # are comments
```

**YAML format** (`wildcards/styles.yaml`):
```yaml
painting:
  - oil painting
  - watercolor
  - gouache
photo:
  - photograph
  - cinematic
```

Reference nested keys with `/`: `__styles/painting__`

## Links

- [sd-dynamic-prompts syntax reference](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/SYNTAX.md)
- [sd-dynamic-prompts](https://github.com/adieyal/sd-dynamic-prompts) — the A1111 equivalent
