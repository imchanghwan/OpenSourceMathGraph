import numpy as np
import sympy as sp
from errors.build_error import BuildError

x = sp.Symbol("x")

def build_graph_data(expr, x_min=-10, x_max=10, num_points=1000) -> tuple[np.ndarray, np.ndarray]:
    f = sp.lambdify(x, expr, "numpy")
    xs = np.linspace(x_min, x_max, num_points)

    try:
        ys = f(xs)
    except Exception as e:
        raise BuildError("그래프 데이터 생성 실패", original=e)

    # scalar 대응
    if np.isscalar(ys):
        ys = np.full_like(xs, ys, dtype=np.float64)
    else:
        ys = np.asarray(ys, dtype=np.float64)

    # NaN / inf 제거
    mask = np.isfinite(xs) & np.isfinite(ys)

    return xs[mask], ys[mask]