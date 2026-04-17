from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Callable
from uuid import uuid4

import numpy as np
import sympy as sp


@dataclass
class FunctionInput:
    expression: str = ""
    color: str = "#2f80ed"
    enabled: bool = True
    id: str = field(default_factory=lambda: uuid4().hex)
    error: str | None = None


@dataclass(frozen=True)
class GraphSegment:
    x: np.ndarray
    y: np.ndarray


@dataclass(frozen=True)
class GraphSeries:
    id: str
    expression: str
    color: str
    segments: list[GraphSegment]


@dataclass(frozen=True)
class CompiledFunction:
    id: str
    expression: str
    color: str
    expr: sp.Expr
    func: Callable


@dataclass(frozen=True)
class RenderCacheEntry:
    series: GraphSeries
    x_min: float
    x_max: float
    y_min: float | None
    y_max: float | None
    sample_count: int
