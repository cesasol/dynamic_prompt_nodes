from __future__ import annotations
import re
from typing import Any

from src.evaluator.context import EvaluationContext


_TOKEN_RE = re.compile(
    r'\s*('
    r'"(?:[^"\\]|\\.)*"|'
    r"'(?:[^'\\]|\\.)*'|"
    r'\(|\)|'
    r',|'
    r'(?:and|or|not|eq|ne|gt|lt|ge|le|contains|in)\b|'
    r'-?\d+|'
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    r')'
)


class _Token:
    def __init__(self, kind: str, value: str) -> None:
        self.kind = kind
        self.value = value


def _tokenize(condition: str) -> list[_Token]:
    tokens: list[_Token] = []
    pos = 0
    while pos < len(condition):
        m = _TOKEN_RE.match(condition, pos)
        if not m:
            raise ValueError(f"Unexpected character in condition: {condition[pos:]!r}")
        raw = m.group(1)
        pos = m.end()
        if raw in ("and", "or", "not"):
            tokens.append(_Token(raw.upper(), raw))
        elif raw in ("eq", "ne", "gt", "lt", "ge", "le", "contains", "in"):
            tokens.append(_Token(raw.upper(), raw))
        elif raw == "(":
            tokens.append(_Token("LPAREN", raw))
        elif raw == ")":
            tokens.append(_Token("RPAREN", raw))
        elif raw == ",":
            tokens.append(_Token("COMMA", raw))
        elif raw.startswith('"') or raw.startswith("'"):
            tokens.append(_Token("STRING", raw[1:-1]))
        elif raw.lstrip("-").isdigit():
            tokens.append(_Token("NUMBER", raw))
        else:
            tokens.append(_Token("WORD", raw))
    return tokens


class _Parser:
    def __init__(self, tokens: list[_Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> _Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, kind: str | None = None) -> _Token:
        token = self.peek()
        if token is None:
            raise ValueError(f"Unexpected end of condition, expected {kind}")
        if kind is not None and token.kind != kind:
            raise ValueError(f"Expected {kind}, got {token.kind} ({token.value!r})")
        self.pos += 1
        return token

    def parse(self) -> "_ASTNode":
        return self._or_expr()

    def _or_expr(self) -> "_ASTNode":
        left = self._and_expr()
        while self.peek() and self.peek().kind == "OR":
            self.consume("OR")
            right = self._and_expr()
            left = _BinOp("or", left, right)
        return left

    def _and_expr(self) -> "_ASTNode":
        left = self._not_expr()
        while self.peek() and self.peek().kind == "AND":
            self.consume("AND")
            right = self._not_expr()
            left = _BinOp("and", left, right)
        return left

    def _not_expr(self) -> "_ASTNode":
        if self.peek() and self.peek().kind == "NOT":
            self.consume("NOT")
            return _UnaryOp("not", self._not_expr())
        return self._primary()

    def _primary(self) -> "_ASTNode":
        if self.peek() and self.peek().kind == "LPAREN":
            self.consume("LPAREN")
            node = self._or_expr()
            self.consume("RPAREN")
            return node
        return self._comparison()

    def _comparison(self) -> "_ASTNode":
        var_token = self.consume("WORD")
        var_node = _VarRef(var_token.value)

        if not self.peek():
            return var_node

        negate = False
        if self.peek().kind == "NOT":
            self.consume("NOT")
            negate = True

        if not self.peek() or self.peek().kind not in (
            "EQ", "NE", "GT", "LT", "GE", "LE", "CONTAINS", "IN",
        ):
            if negate:
                raise ValueError(f"Expected operator after 'not', got {self.peek().value if self.peek() else 'EOF'}")
            return var_node

        op_token = self.consume()
        op = op_token.value
        if negate:
            op = _NEGATED_OPS.get(op, op)

        values = self._value_list()
        return _Comparison(var_node, op, values)

    def _value_list(self) -> list["_ASTNode"]:
        if self.peek() and self.peek().kind == "LPAREN":
            self.consume("LPAREN")
            values: list[_ASTNode] = [self._value()]
            while self.peek() and self.peek().kind == "COMMA":
                self.consume("COMMA")
                values.append(self._value())
            self.consume("RPAREN")
            return values
        return [self._value()]

    def _value(self) -> "_ASTNode":
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of condition, expected value")
        if token.kind == "STRING":
            self.consume()
            return _Literal(token.value)
        if token.kind == "NUMBER":
            self.consume()
            return _Literal(int(token.value))
        if token.kind == "WORD":
            self.consume()
            return _VarRef(token.value)
        raise ValueError(f"Unexpected token {token.kind} ({token.value!r}) in value position")


_NEGATED_OPS = {
    "eq": "ne",
    "ne": "eq",
    "gt": "le",
    "lt": "ge",
    "ge": "lt",
    "le": "gt",
    "contains": "not_contains",
    "in": "not_in",
}


class _ASTNode:
    def evaluate(self, ctx: EvaluationContext, evaluator: Any) -> bool:
        raise NotImplementedError


class _VarRef(_ASTNode):
    def __init__(self, name: str) -> None:
        self.name = name

    def evaluate(self, ctx: EvaluationContext, evaluator: Any) -> bool:
        try:
            val = ctx.get_variable(self.name, None, evaluator)
        except KeyError:
            return False
        return bool(val and val.strip())


class _Literal(_ASTNode):
    def __init__(self, value: str | int) -> None:
        self.value = value

    def evaluate(self, ctx: EvaluationContext, evaluator: Any) -> bool:
        return bool(self.value) if isinstance(self.value, str) else self.value != 0


class _UnaryOp(_ASTNode):
    def __init__(self, op: str, operand: _ASTNode) -> None:
        self.op = op
        self.operand = operand

    def evaluate(self, ctx: EvaluationContext, evaluator: Any) -> bool:
        return not self.operand.evaluate(ctx, evaluator)


class _BinOp(_ASTNode):
    def __init__(self, op: str, left: _ASTNode, right: _ASTNode) -> None:
        self.op = op
        self.left = left
        self.right = right

    def evaluate(self, ctx: EvaluationContext, evaluator: Any) -> bool:
        if self.op == "and":
            return self.left.evaluate(ctx, evaluator) and self.right.evaluate(ctx, evaluator)
        if self.op == "or":
            return self.left.evaluate(ctx, evaluator) or self.right.evaluate(ctx, evaluator)
        raise ValueError(f"Unknown binary operator: {self.op}")


class _Comparison(_ASTNode):
    def __init__(self, var: _VarRef, op: str, values: list[_ASTNode]) -> None:
        self.var = var
        self.op = op
        self.values = values

    def _resolve_value(self, node: _ASTNode, ctx: EvaluationContext, evaluator: Any) -> str | int:
        if isinstance(node, _Literal):
            return node.value
        if isinstance(node, _VarRef):
            try:
                val = ctx.get_variable(node.name, None, evaluator)
            except KeyError:
                return ""
            try:
                return int(val)
            except ValueError:
                return val
        raise ValueError(f"Unexpected value node type: {type(node)}")

    def evaluate(self, ctx: EvaluationContext, evaluator: Any) -> bool:
        try:
            var_val = ctx.get_variable(self.var.name, None, evaluator)
        except KeyError:
            var_val = ""

        try:
            var_num = int(var_val)
        except ValueError:
            var_num = None

        resolved = [self._resolve_value(v, ctx, evaluator) for v in self.values]

        if self.op == "eq":
            return any(str(var_val) == str(v) for v in resolved)
        if self.op == "ne":
            return all(str(var_val) != str(v) for v in resolved)
        if self.op in ("gt", "lt", "ge", "le"):
            if var_num is None:
                return False
            for v in resolved:
                try:
                    v_num = int(v)
                except (ValueError, TypeError):
                    return False
                if self.op == "gt" and not (var_num > v_num):
                    return False
                if self.op == "lt" and not (var_num < v_num):
                    return False
                if self.op == "ge" and not (var_num >= v_num):
                    return False
                if self.op == "le" and not (var_num <= v_num):
                    return False
            return True
        if self.op == "contains":
            for v in resolved:
                if str(v) == str(var_val):
                    return True
            if len(resolved) == 1:
                return str(resolved[0]) in str(var_val)
            return False
        if self.op == "not_contains":
            for v in resolved:
                if str(v) == str(var_val):
                    return False
            if len(resolved) == 1:
                return str(resolved[0]) not in str(var_val)
            return True
        if self.op == "in":
            for v in resolved:
                if str(v) == str(var_val):
                    return True
            return False
        if self.op == "not_in":
            for v in resolved:
                if str(v) == str(var_val):
                    return False
            return True
        raise ValueError(f"Unknown comparison operator: {self.op}")


def evaluate_condition(condition: str, ctx: EvaluationContext, evaluator: Any) -> bool:
    tokens = _tokenize(condition)
    if not tokens:
        return False
    ast = _Parser(tokens).parse()
    return ast.evaluate(ctx, evaluator)
