from __future__ import annotations

from collections.abc import Callable

import sympy as sp


x = sp.Symbol("x")

ALLOWED_FUNCTIONS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "sqrt": sp.sqrt,
    "log": sp.log,
    "exp": sp.exp,
    "abs": sp.Abs,
}

ALLOWED_NAMES = {
    "x": x,
    "pi": sp.pi,
    "E": sp.E,
    "e": sp.E,
    **ALLOWED_FUNCTIONS,
}


def parse_expression(expr_text: str) -> sp.Expr:
    text = normalize_expression(expr_text)
    if not text:
        raise ValueError("Enter an expression.")
    if "__" in text:
        raise ValueError("Double underscore names are not allowed.")

    try:
        expr = sp.sympify(text, locals=ALLOWED_NAMES)
    except Exception as exc:
        raise ValueError(f"Could not parse expression: {exc}") from exc

    if not isinstance(expr, sp.Expr):
        raise ValueError("Expression must be a mathematical expression.")

    unknown_symbols = expr.free_symbols - {x}
    if unknown_symbols:
        names = ", ".join(sorted(str(symbol) for symbol in unknown_symbols))
        raise ValueError(f"Only variable x is supported. Unknown: {names}")

    unknown_functions = [
        fn for fn in expr.atoms(sp.Function) if fn.func not in set(ALLOWED_FUNCTIONS.values())
    ]
    if unknown_functions:
        names = ", ".join(sorted(str(fn.func) for fn in unknown_functions))
        raise ValueError(f"Unsupported function: {names}")

    return expr


def normalize_expression(expr_text: str) -> str:
    return expr_text.strip().replace("^", "**")


def build_function(expr: sp.Expr) -> Callable:
    try:
        return sp.lambdify(x, expr, "numpy")
    except Exception as exc:
        raise ValueError(f"Could not build numeric function: {exc}") from exc
