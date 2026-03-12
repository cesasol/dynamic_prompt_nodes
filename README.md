# Dynamic Prompt Nodes

ComfyUI custom nodes for dynamic prompt generation with full wildcard support, powered by [dynamicprompts](https://github.com/adieyal/dynamicprompts). Aims feature parity with [sd-dynamic-prompts](https://github.com/adieyal/sd-dynamic-prompts) for Automatic1111.

## Features

- **Random sampling** — pick random variants from `{option1|option2|option3}`
- **Wildcards** — substitute values from `.txt` or `.yaml` wildcard files using `__wildcard_name__`
- **Combinatorial generation** — enumerate every possible prompt combination
- **Jinja2 templates** — full imperative prompt logic via Jinja2

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
**Output:** `prompt` (STRING)

### Dynamic Prompt (Jinja2)
Processes a Jinja2 template with access to the full dynamicprompts extension set.

**Inputs:** `template` (STRING), `seed` (INT)
**Output:** `prompt` (STRING)

## Wildcard Syntax

| Syntax | Description |
|--------|-------------|
| `{cat\|dog\|bird}` | Pick one randomly |
| `{2$$cat\|dog\|bird}` | Pick exactly 2 |
| `{1-3$$cat\|dog\|bird}` | Pick 1 to 3 |
| `__animals__` | Substitute from `wildcards/animals.txt` |
| `__colors/warm__` | Substitute from `wildcards/colors/warm.txt` |
| `__colors*__` | Glob match wildcard files |

### Wildcard Files

**Text format** (`wildcards/animals.txt`):
```
cat
dog
bird
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

- [dynamicprompts syntax reference](https://github.com/adieyal/dynamicprompts/blob/main/docs/SYNTAX.md)
- [sd-dynamic-prompts](https://github.com/adieyal/sd-dynamic-prompts) — the A1111 equivalent
