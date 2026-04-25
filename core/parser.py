import sympy as sp

def parse_expression(text: str):
    try:
        expr = sp.simplify(text)
        return expr
    except Exception as e:
        print(f"수식 파싱 오류: {e}")
        return None
