import numpy as np
import sympy as sp
from errors.build_error import BuildError

x = sp.Symbol("x")


def build_graph_data(expr, x_min=-10, x_max=10, y_min=-10, y_max=10, base_points=1000):
    # SymPy 수식을 NumPy 계산 함수로 변환
    f = sp.lambdify(x, expr, "numpy")

    num_points = _calc_num_points(x_min, x_max, base_points)

    # 발산점 탐색 (예: 1/x -> x=0)
    singular_xs = _find_singular_xs(expr, x_min, x_max)

    # 기본 샘플 + 발산점 주변 보조 샘플 생성
    xs = _build_sample_points(x_min, x_max, num_points, singular_xs)

    try:
        ys = f(xs)
    except Exception as e:
        raise BuildError("그래프 데이터 생성 실패", original=e)

    # 상수식 처리 (예: y=3)
    if np.isscalar(ys) or not isinstance(ys, np.ndarray):
        try:
            ys = np.full_like(xs, float(sp.Float(ys)), dtype=np.float64)
        except Exception as e:
            raise BuildError("수식을 float로 변환 실패", original=e)
    else:
        ys = np.asarray(ys, dtype=np.float64)

    # 불연속 구간에 NaN 삽입
    xs, ys = _handle_discontinuity(xs, ys, y_min, y_max, singular_xs)
    return xs, ys


def _handle_discontinuity(xs, ys, y_min=-10, y_max=10, singular_xs=None):
    if len(ys) < 2:
        return xs, ys

    y_range = max(abs(y_max - y_min), 1e-9)
    clip_threshold = max(y_range * 50, 1.0)

    ys_safe = ys.copy().astype(np.float64)

    # pyqtgraph는 NaN 지점에서 선을 끊음
    ys_safe[~np.isfinite(ys_safe)] = np.nan
    ys_safe[np.abs(ys_safe) > clip_threshold] = np.nan

    finite_mask = np.isfinite(ys_safe)
    finite_ys = ys_safe[finite_mask]
    if len(finite_ys) < 2:
        return xs, ys_safe

    # y값 차이가 너무 크면 불연속으로 판단
    dy = np.abs(np.diff(ys_safe))
    threshold = y_range * 2

    opposite_large_values = (
        (ys_safe[:-1] * ys_safe[1:] < 0) &
        (np.abs(ys_safe[:-1]) > y_range) &
        (np.abs(ys_safe[1:]) > y_range)
    )

    discontinuous = (
        ~finite_mask[:-1] |
        ~finite_mask[1:] |
        (dy > threshold) |
        opposite_large_values
    )

    if singular_xs:
        # 발산점이 들어 있는 구간을 한 번에 끊음
        singular_indices = np.searchsorted(xs, singular_xs)
        singular_indices = singular_indices[
            (0 < singular_indices) & (singular_indices < len(xs))
        ]
        discontinuous[singular_indices - 1] = True

    new_xs = xs.copy().astype(np.float64)
    new_ys = ys_safe.copy()

    insert_indices = np.where(discontinuous)[0] + 1
    new_xs = np.insert(new_xs, insert_indices, np.nan)
    new_ys = np.insert(new_ys, insert_indices, np.nan)

    return new_xs, new_ys


def _calc_num_points(x_min: float, x_max: float, base: int = 1000) -> int:
    x_range = x_max - x_min
    scale = 20 / x_range
    points = int(base * np.clip(scale, 0.5, 5.0))
    return points


def _build_sample_points(x_min, x_max, num_points, singular_xs):
    # 기본 x 샘플 생성
    xs = np.linspace(x_min, x_max, num_points)
    if not singular_xs:
        return xs

    x_range = max(abs(x_max - x_min), 1e-9)
    step = x_range / max(num_points - 1, 1)
    offsets = _singularity_offsets(x_range, step, len(singular_xs))
    extra_points = []

    for sx in singular_xs:
        # 발산점 양쪽에 보조 샘플 추가
        for offset in offsets:
            left = sx - offset
            right = sx + offset
            if x_min < left < x_max:
                extra_points.append(left)
            if x_min < right < x_max:
                extra_points.append(right)

    if not extra_points:
        return xs

    xs = np.concatenate([xs, np.array(extra_points, dtype=np.float64)])
    xs = xs[(xs >= x_min) & (xs <= x_max)]
    return np.unique(np.sort(xs))


def _singularity_offsets(x_range, step, singular_count):
    # 발산점이 많으면 보조 샘플 수를 줄임
    if singular_count > 80:
        ratios = [1e-5, 1e-3]
    elif singular_count > 30:
        ratios = [1e-7, 1e-5, 1e-3]
    else:
        ratios = [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]

    relative_offsets = x_range * np.array(ratios, dtype=np.float64)
    offsets = np.concatenate([relative_offsets, np.array([step * 0.25])])
    offsets = offsets[offsets > 0]
    return np.unique(offsets)


def _find_singular_xs(expr, x_min, x_max):
    singulars = []

    try:
        denominator = sp.denom(sp.together(expr))
        if denominator != 1:
            singulars.extend(_real_roots_in_range(denominator, x_min, x_max))
    except Exception:
        pass

    singulars.extend(_trig_singularities_in_range(expr, x_min, x_max))

    return sorted(set(round(value, 12) for value in singulars))


def _real_roots_in_range(poly_expr, x_min, x_max):
    roots = []

    try:
        poly = sp.Poly(poly_expr, x)
        candidates = [root for root in sp.nroots(poly) if abs(sp.im(root)) < 1e-10]
    except Exception:
        try:
            candidates = list(sp.solve(poly_expr, x))
        except Exception:
            candidates = []

    for candidate in candidates:
        real_value = _to_real_float(candidate)
        if real_value is not None and x_min < real_value < x_max:
            roots.append(real_value)

    return roots


def _to_real_float(value):
    try:
        evaluated = complex(sp.N(value))
    except Exception:
        return None

    if abs(evaluated.imag) > 1e-10:
        return None

    real_value = float(evaluated.real)
    if not np.isfinite(real_value):
        return None

    return real_value


def _trig_singularities_in_range(expr, x_min, x_max):
    singulars = []
    rules = [
        (sp.tan, sp.pi / 2, sp.pi),
        (sp.sec, sp.pi / 2, sp.pi),
        (sp.cot, 0, sp.pi),
        (sp.csc, 0, sp.pi),
    ]

    for func, offset, period in rules:
        for node in expr.atoms(func):
            singulars.extend(
                _linear_periodic_points(node.args[0], offset, period, x_min, x_max)
            )

    return singulars


def _linear_periodic_points(arg, offset, period, x_min, x_max):
    try:
        poly = sp.Poly(sp.expand(arg), x)
    except Exception:
        return []

    if poly.degree() != 1:
        return []

    coeffs = poly.all_coeffs()
    a = _to_real_float(coeffs[0])
    b = _to_real_float(coeffs[1])
    if a is None or b is None or abs(a) < 1e-12:
        return []

    lower_k = int(np.floor(_to_real_float((a * x_min + b - offset) / period))) - 1
    upper_k = int(np.ceil(_to_real_float((a * x_max + b - offset) / period))) + 1
    points = []

    for k in range(lower_k, upper_k + 1):
        sx = _to_real_float((offset + k * period - b) / a)
        if sx is not None and x_min < sx < x_max:
            points.append(sx)

    return points
