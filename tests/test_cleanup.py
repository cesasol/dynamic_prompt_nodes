import pytest

from src.nodes.cleanup import cleanup_prompt, _ignore_repeats, _cleanup_extra_spaces, _cleanup_empty_constructs


class TestIgnoreRepeats:
    def test_no_duplicates_unchanged(self):
        assert _ignore_repeats("red hair, blue eyes") == "red hair, blue eyes"

    def test_removes_simple_duplicate(self):
        assert _ignore_repeats("red hair, blue eyes, red hair") == "red hair, blue eyes"

    def test_case_insensitive(self):
        assert _ignore_repeats("Red Hair, BLUE EYES, red hair") == "Red Hair, BLUE EYES"

    def test_preserves_first_casing(self):
        assert _ignore_repeats("red hair, BLUE EYES, Red Hair") == "red hair, BLUE EYES"

    def test_attention_tags_preserved(self):
        assert (
            _ignore_repeats("(blue eyes:1.2), red hair, (blue eyes:1.2)")
            == "(blue eyes:1.2), red hair"
        )

    def test_bracket_tags_preserved(self):
        assert (
            _ignore_repeats("[low quality], red hair, [low quality]")
            == "[low quality], red hair"
        )

    def test_nested_attention_tags(self):
        assert (
            _ignore_repeats("((masterpiece)), red hair, ((masterpiece))")
            == "((masterpiece)), red hair"
        )

    def test_comma_inside_attention_tag_not_split(self):
        prompt = "(red, blue:1.2), green, (red, blue:1.2)"
        assert _ignore_repeats(prompt) == "(red, blue:1.2), green"

    def test_empty_string(self):
        assert _ignore_repeats("") == ""

    def test_single_keyword(self):
        assert _ignore_repeats("red hair") == "red hair"

    def test_trims_whitespace(self):
        assert _ignore_repeats("  red hair  ,  blue eyes  ") == "red hair, blue eyes"


class TestCleanupExtraSpaces:
    def test_collapses_multiple_spaces(self):
        assert _cleanup_extra_spaces("red   hair") == "red hair"

    def test_trims_outer_spaces(self):
        assert _cleanup_extra_spaces("  red hair  ") == "red hair"

    def test_spaces_around_commas(self):
        assert _cleanup_extra_spaces("red hair  ,  blue eyes") == "red hair, blue eyes"

    def test_spaces_inside_parens(self):
        assert _cleanup_extra_spaces("( blue eyes )") == "(blue eyes)"

    def test_spaces_inside_brackets(self):
        assert _cleanup_extra_spaces("[ low quality ]") == "[low quality]"

    def test_empty_string(self):
        assert _cleanup_extra_spaces("") == ""

    def test_tabs_converted_to_spaces(self):
        assert _cleanup_extra_spaces("red\thair") == "red hair"


class TestCleanupEmptyConstructs:
    def test_removes_empty_keyword(self):
        assert _cleanup_empty_constructs("red hair, , blue eyes") == "red hair, blue eyes"

    def test_removes_whitespace_only_keyword(self):
        assert _cleanup_empty_constructs("red hair,   , blue eyes") == "red hair, blue eyes"

    def test_removes_empty_parens(self):
        assert _cleanup_empty_constructs("red hair, (), blue eyes") == "red hair, blue eyes"

    def test_removes_empty_parens_with_spaces(self):
        assert _cleanup_empty_constructs("red hair, (  ), blue eyes") == "red hair, blue eyes"

    def test_removes_empty_brackets(self):
        assert _cleanup_empty_constructs("red hair, [], blue eyes") == "red hair, blue eyes"

    def test_removes_empty_brackets_with_spaces(self):
        assert _cleanup_empty_constructs("red hair, [  ], blue eyes") == "red hair, blue eyes"

    def test_removes_nested_empty_tags(self):
        assert _cleanup_empty_constructs("red hair, ((  )), blue eyes") == "red hair, blue eyes"

    def test_keeps_non_empty_tags(self):
        assert _cleanup_empty_constructs("(blue eyes:1.2), red hair") == "(blue eyes:1.2), red hair"

    def test_empty_string(self):
        assert _cleanup_empty_constructs("") == ""

    def test_all_empty_returns_empty(self):
        assert _cleanup_empty_constructs(" , , ") == ""


class TestCleanupPrompt:
    def test_all_flags_false_no_change(self):
        prompt = "red hair  ,  red hair , ()"
        assert cleanup_prompt(prompt) == prompt

    def test_all_flags_combined(self):
        prompt = "  red hair  ,  red hair  ,  ()  ,  blue eyes  "
        result = cleanup_prompt(
            prompt,
            ignore_repeats=True,
            cleanup_extra_spaces=True,
            cleanup_empty_constructs=True,
        )
        assert result == "red hair, blue eyes"

    def test_only_ignore_repeats(self):
        prompt = "red hair, red hair, blue eyes"
        result = cleanup_prompt(prompt, ignore_repeats=True)
        assert result == "red hair, blue eyes"

    def test_only_cleanup_spaces(self):
        prompt = "  red hair  ,  blue eyes  "
        result = cleanup_prompt(prompt, cleanup_extra_spaces=True)
        assert result == "red hair, blue eyes"

    def test_only_cleanup_empty(self):
        prompt = "red hair, (), blue eyes"
        result = cleanup_prompt(prompt, cleanup_empty_constructs=True)
        assert result == "red hair, blue eyes"

    def test_combines_spaces_and_empty(self):
        prompt = "  red hair  ,  ()  ,  blue eyes  "
        result = cleanup_prompt(
            prompt,
            cleanup_extra_spaces=True,
            cleanup_empty_constructs=True,
        )
        assert result == "red hair, blue eyes"

    def test_complex_prompt(self):
        prompt = "  (masterpiece:1.2)  ,  red hair  ,  red hair  ,  [low quality]  ,  ()  ,  ((  ))  ,  blue eyes  "
        result = cleanup_prompt(
            prompt,
            ignore_repeats=True,
            cleanup_extra_spaces=True,
            cleanup_empty_constructs=True,
        )
        assert result == "(masterpiece:1.2), red hair, [low quality], blue eyes"
