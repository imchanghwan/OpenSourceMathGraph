from __future__ import annotations

from collections.abc import Callable
import warnings

import numpy as np

from app.config import DEFAULT_SAMPLE_POINTS
from app.models import GraphSegment


def generate_segments(
    func: Callable,
    x_min: float,
    x_max: float,
    y_min: float | None = None,
    y_max: float | None = None,
    num_points: int = DEFAULT_SAMPLE_POINTS,
) -> list[GraphSegment]:
    if x_min >= x_max:
        raise ValueError("x_min must be smaller than x_max.")
    if num_points < 2:
        raise ValueError("num_points must be at least 2.")

    xs = np.linspace(x_min, x_max, num_points, dtype=float)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        try:
            ys = func(xs)
        except Exception as exc:
            raise ValueError(f"Could not evaluate expression: {exc}") from exc

    ys = _normalize_y_values(ys, xs)
    finite = np.isfinite(xs) & np.isfinite(ys)

    if not np.any(finite):
        return []

    segments: list[GraphSegment] = []
    for start, end in _contiguous_true_ranges(finite):
        x_part = xs[start:end]
        y_part = ys[start:end]
        segments.extend(_split_large_jumps(x_part, y_part, y_min, y_max))

    return [segment for segment in segments if len(segment.x) >= 2]


def adaptive_sample_count(
    pixel_width: int,
    samples_per_pixel: float,
    min_points: int,
    max_points: int,
) -> int:
    if pixel_width <= 0:
        return min_points
    count = int(pixel_width * samples_per_pixel)
    return max(min_points, min(count, max_points))


def expanded_x_range(x_min: float, x_max: float, overscan_ratio: float) -> tuple[float, float]:
    width = x_max - x_min
    if width <= 0:
        return x_min, x_max
    padding = width * max(0.0, overscan_ratio)
    return x_min - padding, x_max + padding


def sample_count_for_range(
    visible_sample_count: int,
    visible_x_min: float,
    visible_x_max: float,
    sample_x_min: float,
    sample_x_max: float,
    max_points: int,
) -> int:
    visible_width = visible_x_max - visible_x_min
    sample_width = sample_x_max - sample_x_min
    if visible_width <= 0 or sample_width <= 0:
        return visible_sample_count

    scaled_count = int(visible_sample_count * (sample_width / visible_width))
    return max(visible_sample_count, min(scaled_count, max_points))


def robust_y_limits(
    segments: list[GraphSegment],
    visible_x_min: float,
    visible_x_max: float,
    percentile_low: float,
    percentile_high: float,
    padding_ratio: float,
    min_span: float,
) -> tuple[float, float] | None:
    values: list[np.ndarray] = []
    for segment in segments:
        visible = (
            (segment.x >= visible_x_min)
            & (segment.x <= visible_x_max)
            & np.isfinite(segment.y)
        )
        if np.any(visible):
            values.append(segment.y[visible])

    if not values:
        return None

    ys = np.concatenate(values)
    ys = ys[np.isfinite(ys)]
    if len(ys) == 0:
        return None

    low = float(np.nanpercentile(ys, percentile_low))
    high = float(np.nanpercentile(ys, percentile_high))
    if not np.isfinite(low) or not np.isfinite(high):
        return None

    if low == high:
        center = low
        half_span = max(min_span / 2.0, abs(center) * 0.1, 1.0)
        return center - half_span, center + half_span

    span = max(high - low, min_span)
    center = (low + high) / 2.0
    padded_half_span = (span * (1.0 + max(0.0, padding_ratio))) / 2.0
    return center - padded_half_span, center + padded_half_span


def _normalize_y_values(ys, xs: np.ndarray) -> np.ndarray:
    if np.isscalar(ys):
        return np.full_like(xs, float(ys), dtype=float)

    arr = np.asarray(ys)
    if arr.shape == ():
        return np.full_like(xs, float(arr), dtype=float)

    if np.iscomplexobj(arr):
        real = np.real(arr)
        imag = np.imag(arr)
        arr = np.where(np.abs(imag) < 1e-9, real, np.nan)

    try:
        return np.asarray(arr, dtype=float)
    except (TypeError, ValueError):
        return np.full_like(xs, np.nan, dtype=float)


def _contiguous_true_ranges(mask: np.ndarray) -> list[tuple[int, int]]:
    padded = np.concatenate(([False], mask, [False]))
    changes = np.flatnonzero(padded[1:] != padded[:-1])
    return list(zip(changes[0::2], changes[1::2]))


def _split_large_jumps(
    xs: np.ndarray,
    ys: np.ndarray,
    y_min: float | None,
    y_max: float | None,
) -> list[GraphSegment]:
    if len(xs) < 2:
        return []

    if y_min is not None and y_max is not None and y_max > y_min:
        jump_threshold = max((y_max - y_min) * 1.5, 25.0)
    else:
        jump_threshold = _robust_jump_threshold(ys)

    y_delta = np.abs(np.diff(ys))
    sign_cross = np.signbit(ys[:-1]) != np.signbit(ys[1:])
    near_asymptote = np.maximum(np.abs(ys[:-1]), np.abs(ys[1:])) > jump_threshold
    jump_indexes = np.flatnonzero((y_delta > jump_threshold) | (sign_cross & near_asymptote)) + 1
    split_points = [0, *jump_indexes.tolist(), len(xs)]

    segments: list[GraphSegment] = []
    for start, end in zip(split_points[:-1], split_points[1:]):
        if end - start >= 2:
            segments.append(GraphSegment(x=xs[start:end], y=ys[start:end]))

    return segments


def _robust_jump_threshold(ys: np.ndarray) -> float:
    finite = ys[np.isfinite(ys)]
    if len(finite) < 4:
        return 25.0

    q1, q3 = np.nanpercentile(finite, [25, 75])
    iqr = q3 - q1
    p5, p95 = np.nanpercentile(finite, [5, 95])
    robust_span = max(float(iqr * 6.0), float((p95 - p5) * 1.5), 25.0)
    return robust_span if np.isfinite(robust_span) else 25.0
