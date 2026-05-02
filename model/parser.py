import sympy as sp

from errors.parse_error import ParseError

def parse_expression(text: str):
    try:
        # "y = x**2" → "x**2" 전처리
        if "=" in text:
            _, rhs = text.split("=", 1)  # 등호 기준 오른쪽만 사용
            text = rhs.strip()

        expr = sp.simplify(text)
        return expr
    except Exception as e:
        raise ParseError(f"수식 파싱 실패: '{text}'", original=e)