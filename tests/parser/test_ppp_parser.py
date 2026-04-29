from src.parser.parser import parse
from src.parser.ast_nodes import Template, Text, PPPSet, PPPEcho, PPPIf, Variant, PPPSendToNegative, PPPExtraNetwork


def test_ppp_set_parses():
    result = parse("<ppp:set x>hello<ppp:/set>")
    assert len(result.parts) == 1
    node = result.parts[0]
    assert isinstance(node, PPPSet)
    assert node.var_name == "x"
    assert node.modifiers == []
    assert node.content.parts[0].value == "hello"


def test_ppp_set_with_modifiers():
    result = parse("<ppp:set x evaluate add>hello<ppp:/set>")
    node = result.parts[0]
    assert isinstance(node, PPPSet)
    assert node.var_name == "x"
    assert node.modifiers == ["evaluate", "add"]


def test_ppp_echo_self_closing():
    result = parse("<ppp:echo x/>")
    assert len(result.parts) == 1
    node = result.parts[0]
    assert isinstance(node, PPPEcho)
    assert node.var_name == "x"
    assert node.default is None


def test_ppp_echo_with_default():
    result = parse("<ppp:echo x>fallback<ppp:/echo>")
    node = result.parts[0]
    assert isinstance(node, PPPEcho)
    assert node.var_name == "x"
    assert node.default is not None
    assert node.default.parts[0].value == "fallback"


def test_ppp_if_simple():
    result = parse("<ppp:if x>matched<ppp:/if>")
    assert len(result.parts) == 1
    node = result.parts[0]
    assert isinstance(node, PPPIf)
    assert len(node.branches) == 1
    assert node.branches[0][0] == "x"
    assert node.branches[0][1].parts[0].value == "matched"
    assert node.else_content is None


def test_ppp_if_with_else():
    result = parse("<ppp:if x>a<ppp:else>b<ppp:/if>")
    node = result.parts[0]
    assert isinstance(node, PPPIf)
    assert len(node.branches) == 1
    assert node.else_content is not None
    assert node.else_content.parts[0].value == "b"


def test_ppp_if_with_elif():
    result = parse("<ppp:if x eq 1>a<ppp:elif x eq 2>b<ppp:/if>")
    node = result.parts[0]
    assert isinstance(node, PPPIf)
    assert len(node.branches) == 2
    assert node.branches[0][0] == "x eq 1"
    assert node.branches[1][0] == "x eq 2"
    assert node.else_content is None


def test_ppp_if_with_elif_and_else():
    result = parse("<ppp:if x eq 1>a<ppp:elif x eq 2>b<ppp:else>c<ppp:/if>")
    node = result.parts[0]
    assert isinstance(node, PPPIf)
    assert len(node.branches) == 2
    assert node.else_content is not None
    assert node.else_content.parts[0].value == "c"


def test_ppp_tag_in_text():
    result = parse("before <ppp:set x>hello<ppp:/set> after")
    assert len(result.parts) == 3
    assert isinstance(result.parts[0], Text)
    assert isinstance(result.parts[1], PPPSet)
    assert isinstance(result.parts[2], Text)


def test_ppp_nested_in_variant():
    result = parse("{a|<ppp:if x>b<ppp:/if>}")
    v = result.parts[0]
    assert isinstance(v, Variant)
    assert len(v.options) == 2
    assert isinstance(v.options[1].node.parts[0], PPPIf)


def test_ppp_stn_paired():
    result = parse("<ppp:stn e>content<ppp:/stn>")
    node = result.parts[0]
    assert isinstance(node, PPPSendToNegative)
    assert node.position == "e"
    assert node.content.parts[0].value == "content"
    assert not node.is_insertion_point


def test_ppp_stn_self_closing():
    result = parse("<ppp:stn i0/>")
    node = result.parts[0]
    assert isinstance(node, PPPSendToNegative)
    assert node.position == "i0"
    assert node.is_insertion_point


def test_ppp_stn_no_position():
    result = parse("<ppp:stn>content<ppp:/stn>")
    node = result.parts[0]
    assert isinstance(node, PPPSendToNegative)
    assert node.position is None
    assert node.content.parts[0].value == "content"


def test_ppp_ext_paired():
    result = parse("<ppp:ext lora test_lora 0.5>trigger<ppp:/ext>")
    node = result.parts[0]
    assert isinstance(node, PPPExtraNetwork)
    assert node.ext_type == "lora"
    assert node.name == "test_lora"
    assert node.weight == "0.5"
    assert node.triggers.parts[0].value == "trigger"
    assert not node.is_mapping


def test_ppp_ext_self_closing():
    result = parse("<ppp:ext lora test_lora/>")
    node = result.parts[0]
    assert isinstance(node, PPPExtraNetwork)
    assert node.ext_type == "lora"
    assert node.name == "test_lora"
    assert node.weight is None
    assert node.triggers is None


def test_ppp_ext_with_condition():
    result = parse('<ppp:ext lora test_lora if _is_pony>trigger<ppp:/ext>')
    node = result.parts[0]
    assert isinstance(node, PPPExtraNetwork)
    assert node.ext_type == "lora"
    assert node.name == "test_lora"
    assert node.condition == "_is_pony"
    assert node.triggers.parts[0].value == "trigger"


def test_ppp_ext_quoted_name():
    result = parse("<ppp:ext lora 'test lora' 0.5/>")
    node = result.parts[0]
    assert isinstance(node, PPPExtraNetwork)
    assert node.name == "test lora"
    assert node.weight == "0.5"
