# Roadmap

## ComfyUI Prompt Encoding Reference

This document captures the behavior of ComfyUI's CLIP text encoding pipeline for SDXL-family models (SDXL, Pony, Illustrious) and how our dynamic prompt nodes interact with these constructs.

### BREAK Keyword

**ComfyUI Core Behavior**: Treated as the literal word "BREAK". It is NOT used for prompt splitting or chunking.

- ComfyUI splits prompts only when exceeding the 77-token limit (automatic chunking)
- Unlike A1111/WebUI, BREAK does NOT force a new 75-token chunk with empty-token padding
- To achieve prompt splitting in ComfyUI, users must use custom nodes (e.g., "CLIP Text Encode with BREAK") or `ConditioningConcat` nodes in the graph

**Our Codebase Status**: BREAK is not handled specially. It is parsed as literal text and passed through verbatim to the CLIP encoder.

### AND Keyword

**ComfyUI Core Behavior**: Treated as the literal word "and". It is NOT used for prompt composition or region prompting.

- ComfyUI handles prompt composition through graph nodes (`ConditioningCombine`, `ConditioningAverage`) rather than text syntax
- There is no native "AND" text construct in ComfyUI's standard `CLIPTextEncode` node

**Our Codebase Status**: AND is recognized only inside `<ppp:if>` conditional expressions as a boolean operator (e.g., `<ppp:if _is_pony and _is_sdxl>`). As a prompt construct, it is passed through verbatim as literal text.

### [] Brackets (A1111 De-emphasis)

**ComfyUI Core Behavior**: Passed through as literal characters `[` and `]`. NOT interpreted as weighting or de-emphasis.

- ComfyUI uses `(text:weight)` syntax for attention weighting (e.g., `(masterpiece:1.2)`)
- A1111-style `[low quality]` (meaning reduce weight by ~10%) has no native equivalent
- Custom "A1111 Prompt Parser" nodes can translate `[text]` to `(text:0.9)` or similar

**Our Codebase Status**: `[]` brackets are not parsed as special syntax. Our cleanup layer (`src/nodes/cleanup.py`) can detect and remove empty bracket constructs (`[]`, `[  ]`, `((  ))`) when `cleanup_empty_constructs` is enabled, but does not interpret bracket contents as weight modifiers. They are passed through as literal characters.

### Attention Weighting: () vs [] vs (text:weight)

| Syntax | A1111/WebUI Meaning | ComfyUI Core Meaning | Our Status |
|---|---|---|---|
| `(text)` | Increase weight 1.1x | Increase weight 1.1x (native) | Passed through |
| `((text))` | Increase weight 1.21x | Increase weight 1.21x (native) | Passed through |
| `(text:1.5)` | Set weight to 1.5 | Set weight to 1.5 (native) | Passed through |
| `[text]` | Decrease weight 0.9x | Literal `[` and `]` | Passed through literally |
| `[[text]]` | Decrease weight 0.81x | Literal `[` and `]` | Passed through literally |
| `BREAK` | Force new token chunk | Literal word "BREAK" | Passed through literally |
| `AND` | Combine prompts / region | Literal word "and" | Passed through literally (except in `<ppp:if>` conditions) |

### Model-Specific Notes (SDXL / Pony / Illustrious)

All three models use `SDXLClipModel` wrapping dual encoders (CLIP-L and CLIP-G). Both encoders inherit the same `SDTokenizer` base class, meaning the lack of BREAK/AND/[] support is consistent across all SDXL-family models in ComfyUI core.

- **SDXL**: Uses both CLIP-L and CLIP-G; prompts are encoded separately and concatenated
- **Pony**: SDXL-based; uses the same dual-encoder pipeline
- **Illustrious**: SDXL-based; uses the same dual-encoder pipeline

### Future Considerations

If A1111-style compatibility is desired, the following could be implemented:

1. **BREAK translation**: Convert `BREAK` into explicit chunk boundaries or emit multiple output strings for `ConditioningConcat`
2. **AND translation**: Convert `AND` into separate conditioning outputs for `ConditioningCombine`
3. **[] bracket translation**: Convert `[text]` to `(text:0.9)` and `[[text]]` to `(text:0.81)` during cleanup
4. **Custom encoder node**: Wrap our output with a node that replicates A1111 tokenization behavior

These would require extending the grammar, AST, or cleanup layer rather than changing the core evaluator logic.
