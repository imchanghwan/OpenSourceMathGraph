from __future__ import annotations

from app.qt_setup import prepare_qt_runtime

prepare_qt_runtime()

import pyqtgraph as pg
import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QPainter

from app.config import CURVE_PEN_WIDTH
from app.models import GraphSeries
from app.theme import DARK_THEME

pg.setConfigOptions(antialias=True)


class GraphWidget(pg.PlotWidget):
    visible_range_changed = Signal(float, float, float, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._items_by_series: dict[str, pg.PlotDataItem] = {}
        self._suppress_range_signal = False

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setBackground(DARK_THEME["plot_bg"])
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setLabel("bottom", "x", color=DARK_THEME["plot_axis"])
        self.setLabel("left", "y", color=DARK_THEME["plot_axis"])
        self._legend = self.addLegend(offset=(10, 10))
        self._legend.setBrush(pg.mkBrush(QColor(DARK_THEME["legend_bg"])))
        self._legend.setPen(pg.mkPen(QColor(DARK_THEME["panel_border"])))

        plot_item = self.getPlotItem()
        plot_item.setMenuEnabled(False)
        plot_item.showAxes(True)
        plot_item.getAxis("bottom").setPen(pg.mkPen(QColor(DARK_THEME["plot_axis"])))
        plot_item.getAxis("bottom").setTextPen(pg.mkPen(QColor(DARK_THEME["plot_axis"])))
        plot_item.getAxis("left").setPen(pg.mkPen(QColor(DARK_THEME["plot_axis"])))
        plot_item.getAxis("left").setTextPen(pg.mkPen(QColor(DARK_THEME["plot_axis"])))

        view_box = plot_item.getViewBox()
        view_box.setMouseEnabled(x=True, y=True)
        view_box.enableAutoRange(x=False, y=False)
        view_box.sigRangeChanged.connect(self._emit_visible_range)

    def set_view_range(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        emit: bool = True,
    ) -> None:
        self._suppress_range_signal = not emit
        view_box = self.getPlotItem().getViewBox()
        previous_block_state = view_box.blockSignals(not emit)
        try:
            self.setXRange(x_min, x_max, padding=0)
            self.setYRange(y_min, y_max, padding=0)
        finally:
            view_box.blockSignals(previous_block_state)
            self._suppress_range_signal = False

    def set_y_range(self, y_min: float, y_max: float, emit: bool = True) -> None:
        self._suppress_range_signal = not emit
        view_box = self.getPlotItem().getViewBox()
        previous_block_state = view_box.blockSignals(not emit)
        try:
            self.setYRange(y_min, y_max, padding=0)
        finally:
            view_box.blockSignals(previous_block_state)
            self._suppress_range_signal = False

    def update_series(self, series_list: list[GraphSeries]) -> None:
        active_ids = {series.id for series in series_list}
        for stale_id in set(self._items_by_series) - active_ids:
            self._remove_series(stale_id)

        for series in series_list:
            self._update_one_series(series)

    def series_ids(self) -> set[str]:
        return set(self._items_by_series)

    def visible_range(self) -> tuple[float, float, float, float]:
        (x_min, x_max), (y_min, y_max) = self.getPlotItem().getViewBox().viewRange()
        return float(x_min), float(x_max), float(y_min), float(y_max)

    def plot_pixel_width(self) -> int:
        width = self.getPlotItem().getViewBox().width()
        return max(1, int(width))

    def _update_one_series(self, series: GraphSeries) -> None:
        item = self._items_by_series.get(series.id)
        if item is None:
            item = pg.PlotDataItem()
            item.setClipToView(True)
            item.setDownsampling(auto=False)
            self.addItem(item)
            self._items_by_series[series.id] = item

        x_values, y_values = self._merge_segments(series)
        pen = pg.mkPen(QColor(series.color), width=CURVE_PEN_WIDTH)
        pen.setCosmetic(True)
        item.setData(x_values, y_values, pen=pen, name=series.expression)
        self._refresh_legend_label(item, series.expression)

    def _remove_series(self, series_id: str) -> None:
        item = self._items_by_series.pop(series_id)
        self._legend.removeItem(item)
        self.removeItem(item)

    def _refresh_legend_label(self, item: pg.PlotDataItem, name: str) -> None:
        for sample, label in self._legend.items:
            if sample.item is item:
                label.setText(name, color=DARK_THEME["text"])
                return
        self._legend.addItem(item, name)
        self._legend.items[-1][1].setText(name, color=DARK_THEME["text"])

    def _emit_visible_range(self, *_) -> None:
        if self._suppress_range_signal:
            return
        self.visible_range_changed.emit(*self.visible_range())

    def _merge_segments(self, series: GraphSeries) -> tuple[np.ndarray, np.ndarray]:
        if not series.segments:
            return np.array([], dtype=float), np.array([], dtype=float)

        x_parts: list[np.ndarray] = []
        y_parts: list[np.ndarray] = []
        gap = np.array([np.nan], dtype=float)

        for index, segment in enumerate(series.segments):
            if index:
                x_parts.append(gap)
                y_parts.append(gap)
            x_parts.append(segment.x)
            y_parts.append(segment.y)

        return np.concatenate(x_parts), np.concatenate(y_parts)
