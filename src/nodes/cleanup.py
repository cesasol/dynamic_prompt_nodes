from __future__ import annotations

import re


def cleanup_prompt(
    prompt: str,
    *,
    ignore_repeats: bool = False,
    cleanup_extra_spaces: bool = False,
    cleanup_empty_constructs: bool = False,
) -> str:
    """Apply selected cleanup operations to a prompt string."""
    if cleanup_extra_spaces:
        prompt = _cleanup_extra_spaces(prompt)
    if cleanup_empty_constructs:
        prompt = _cleanup_empty_constructs(prompt)
    if ignore_repeats:
        prompt = _ignore_repeats(prompt)
    return prompt


def _tokenize_keywords(prompt: str) -> list[str]:
    """Split prompt into comma-separated keywords respecting nesting of () and []."""
    tokens: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in prompt:
        if ch in "([":
            depth += 1
            current.append(ch)
        elif ch in ")]":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            tokens.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current or (not tokens and not prompt):
        tokens.append("".join(current))
    return tokens


def _ignore_repeats(prompt: str) -> str:
    tokens = _tokenize_keywords(prompt)
    seen: set[str] = set()
    result: list[str] = []
    for raw in tokens:
        normalized = raw.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(raw.strip())
    return ", ".join(result)


def _cleanup_extra_spaces(prompt: str) -> str:
    prompt = prompt.strip()
    prompt = re.sub(r"[ \t]+", " ", prompt)
    prompt = re.sub(r"[ \t]*,[ \t]*", ", ", prompt)
    prompt = re.sub(r"\(\s+", "(", prompt)
    prompt = re.sub(r"\[\s+", "[", prompt)
    prompt = re.sub(r"\s+\)", ")", prompt)
    prompt = re.sub(r"\s+\]", "]", prompt)
    return prompt


def _cleanup_empty_constructs(prompt: str) -> str:
    tokens = _tokenize_keywords(prompt)
    result: list[str] = []
    for raw in tokens:
        stripped = raw.strip()
        if not stripped:
            continue
        if re.fullmatch(r"[\[(]+[\s]*[\])]+", stripped):
            continue
        result.append(raw.strip())
    return ", ".join(result)
