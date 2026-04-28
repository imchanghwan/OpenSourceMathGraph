import sympy as sp

from errors.parse_error import ParseError

def parse_expression(text: str):
    try:
        expr = sp.simplify(text)
        return expr
    except Exception as e:
        raise ParseError("수식 파싱 실패", original=e)