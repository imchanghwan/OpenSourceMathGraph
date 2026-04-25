import numpy as np
import sympy as sp

x = sp.Symbol("x")

def build_graph_data(expr) -> tuple[np.ndarray, np.ndarray]:
    try:
        f = sp.lambdify(x, expr, "numpy")
        xs = np.linspace(-10, 10, 1000)
        ys = f(xs)

        ys = np.asarray(ys, dtype=np.float64)
        mask = np.isfinite(xs) & np.isfinite(ys)

        return xs[mask], ys[mask]
    except Exception as e:
        print(f"그래프 데이터 생성 오류: {e}")
        return None, None