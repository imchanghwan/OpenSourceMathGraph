from __future__ import annotations

from html import escape


def format_expression_html(expression: str) -> str:
    text = expression.strip()
    if not text:
        return '<span class="empty">y = ...</span>'

    return f"y = { _format_math_fragment(text) }"


def _format_math_fragment(text: str) -> str:
    output: list[str] = []
    index = 0

    while index < len(text):
        if text.startswith("**", index):
            exponent, index = _read_exponent(text, index + 2)
            output.append(f"<sup>{_format_math_fragment(exponent)}</sup>")
            continue

        if text[index] == "^":
            exponent, index = _read_exponent(text, index + 1)
            output.append(f"<sup>{_format_math_fragment(exponent)}</sup>")
            continue

        char = text[index]
        if char == "*":
            output.append("&middot;")
        elif char == "π":
            output.append("&pi;")
        else:
            output.append(escape(char))
        index += 1

    return "".join(output).replace("pi", "&pi;")


def _read_exponent(text: str, start: int) -> tuple[str, int]:
    index = _skip_spaces(text, start)
    if index >= len(text):
        return "?", index

    if text[index] == "(":
        return _read_parenthesized(text, index)

    sign_start = index
    if text[index] in "+-":
        index += 1

    while index < len(text) and (
        text[index].isalnum() or text[index] in "._"
    ):
        index += 1

    if index == sign_start or (index == sign_start + 1 and text[sign_start] in "+-"):
        return text[sign_start : sign_start + 1], sign_start + 1

    return text[sign_start:index], index


def _read_parenthesized(text: str, start: int) -> tuple[str, int]:
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    return text[start + 1 :], len(text)


def _skip_spaces(text: str, start: int) -> int:
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    return index
