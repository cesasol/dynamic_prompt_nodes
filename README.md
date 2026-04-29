# Dynamic Prompt Nodes

ComfyUI custom nodes for dynamic prompt generation with full wildcard and variable support. Implements the [sd-dynamic-prompts syntax](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/SYNTAX.md) natively — no external generator dependency.

## Features

- **Random sampling** — pick random variants from `{option1|option2|option3}`
- **Combinatorial generation** — enumerate every possible prompt combination
- **Cyclical sampling** — cycle through options in order across generations
- **Wildcards** — substitute values from `.txt` or `.yaml` wildcard files using `__wildcard_name__`
- **Variables** — define and reuse values within a prompt via `${name=value}`
- **PPP tags** — full support for `<ppp:set>`, `<ppp:echo>`, `<ppp:if>`, `<ppp:stn>`, and `<ppp:ext>` tags from sd-webui-prompt-postprocessor
- **Model family inference** — auto-detects SD1, SDXL, SD3, or Flux from the model input
- **Model variant override** — manually specify Pony, Illustrious, Anima, or NoobAI variants for conditional tags
- **Prompt cleanup** — optional duplicate removal, extra space normalization, and empty construct cleanup
- **Negative prompt collection** — `<ppp:stn>` content is automatically collected and merged into the negative prompt output

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

### Prompt with Wildcards
Advanced prompt processor with full PPP tag support, model family inference, and optional cleanup. Processes both positive and negative templates simultaneously.

**Inputs:**
- `model` (MODEL) — model input for family inference
- `positive_template` (STRING, multiline) — positive prompt template
- `negative_template` (STRING, multiline) — negative prompt template
- `seed` (INT) — random seed for reproducible generation
- `ignore_repeats` (BOOLEAN) — remove duplicate keywords
- `cleanup_extra_spaces` (BOOLEAN) — normalize whitespace
- `cleanup_empty_constructs` (BOOLEAN) — remove empty keywords and attention tags
- `model_variant` (STRING, optional) — override variant: `pony`, `illustrious`, `anima`, `noobai`

**Outputs:** `positive` (STRING), `negative` (STRING)

**Model Family Auto-Detection:**
- SD1 — `diffusion_model.input_blocks` length of 8
- SDXL — `diffusion_model.input_blocks` length of 9
- SD3 — `diffusion_model.in_channels` of 16
- Flux — `diffusion_model.img_in` attribute present

**System Variables (available in `<ppp:if>` conditions):**
- `_is_sd1`, `_is_sdxl`, `_is_sd3`, `_is_flux` — base architecture
- `_is_pony`, `_is_illustrious`, `_is_anima`, `_is_noobai` — variant flags
- `_is_sd` — true for SD1, SDXL, SD3, and their variants

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

### PPP Tags (sd-webui-prompt-postprocessor)

Full support for `<ppp:>` tags. These are evaluated during prompt processing and can control output dynamically.

| Tag | Description |
|-----|-------------|
| `<ppp:set var=x>${value}</ppp:set>` | Set variable `x` to the evaluated content |
| `<ppp:set var=x evaluate>${value}</ppp:set>` | Set variable `x` to the evaluated string (not AST) |
| `<ppp:set var=x add>${value}</ppp:set>` | Append to existing variable `x` |
| `<ppp:set var=x ifundefined>${value}</ppp:set>` | Set only if `x` is not already defined |
| `<ppp:echo var=x />` | Output the value of variable `x` |
| `<ppp:echo var=x>fallback</ppp:echo>` | Output `x` or fallback if undefined |
| `<ppp:if x eq 1>${content}</ppp:if>` | Conditional block with comparison |
| `<ppp:if x eq 1>${a}</ppp:elif x eq 2>${b}</ppp:else>${c}</ppp:if>` | If/elif/else chain |
| `<ppp:stn>${neg_content}</ppp:stn>` | Send content to negative prompt (start position) |
| `<ppp:stn e>${neg_content}</ppp:stn>` | Send content to negative prompt (end position) |
| `<ppp:ext lora="name" weight="0.8" />` | Generate `<lora:name:0.8>` tag |
| `<ppp:ext lora="name" triggers="tag1, tag2" />` | Generate LoRA tag with trigger words |

**Condition Operators for `<ppp:if>`:**
- `eq`, `ne`, `gt`, `lt`, `ge`, `le` — numeric comparisons
- `contains` — substring match
- `in` — value in comma-separated list
- `and`, `or`, `not` — logical combinators
- Parentheses `()` for grouping

**Model Family Conditions:**
```
<ppp:if _is_pony>score_9, score_8_up, score_7_up</ppp:if>
<ppp:if _is_sdxl and not _is_pony>masterpiece, best quality</ppp:if>
```

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
- [sd-webui-prompt-postprocessor syntax](https://github.com/acorderob/sd-webui-prompt-postprocessor/blob/main/docs/SYNTAX.md) — PPP tag reference
- [sd-webui-prompt-postprocessor](https://github.com/acorderob/sd-webui-prompt-postprocessor) — the A1111 PPP equivalent
- [ROADMAP.md](ROADMAP.md) — ComfyUI encoding behavior reference for BREAK, AND, and `[]` brackets
