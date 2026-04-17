from __future__ import annotations

from app.qt_setup import prepare_qt_runtime

prepare_qt_runtime()

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QDoubleValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.config import (
    APP_TITLE,
    AUTO_Y_MIN_SPAN,
    AUTO_Y_PADDING_RATIO,
    AUTO_Y_PERCENTILE_HIGH,
    AUTO_Y_PERCENTILE_LOW,
    DEFAULT_EXPRESSIONS,
    DEFAULT_X_MAX,
    DEFAULT_X_MIN,
    DEFAULT_Y_MAX,
    DEFAULT_Y_MIN,
    MAX_SAMPLE_POINTS,
    MIN_SAMPLE_POINTS,
    PLOT_COLORS,
    RENDER_CACHE_SAMPLE_TOLERANCE,
    SAMPLES_PER_PIXEL,
    UPDATE_DEBOUNCE_MS,
    VIEWPORT_RENDER_DEBOUNCE_MS,
    VIEWPORT_X_OVERSCAN_RATIO,
)
from app.graph_engine import (
    adaptive_sample_count,
    expanded_x_range,
    generate_segments,
    robust_y_limits,
    sample_count_for_range,
)
from app.graph_widget import GraphWidget
from app.math_display import format_expression_html
from app.models import CompiledFunction, FunctionInput, GraphSeries, RenderCacheEntry
from app.parser import build_function, parse_expression
from app.theme import DARK_THEME, app_stylesheet


class ExpressionRow(QWidget):
    changed = Signal()
    remove_requested = Signal(str)

    def __init__(self, model: FunctionInput, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("expressionRow")
        self.model = model

        self.enabled_box = QCheckBox()
        self.enabled_box.setChecked(model.enabled)
        self.enabled_box.setToolTip("Show or hide this expression")

        self.color_button = QToolButton()
        self.color_button.setFixedSize(18, 18)
        self.color_button.setToolTip("Choose graph color")
        self._apply_color_style()

        self.expression_edit = QLineEdit(model.expression)
        self.expression_edit.setPlaceholderText("x**2, sin(x), sqrt(x), 1/x")

        self.math_preview = QLabel()
        self.math_preview.setObjectName("mathPreview")
        self.math_preview.setTextFormat(Qt.RichText)
        self.math_preview.setWordWrap(True)
        self._update_math_preview()

        self.remove_button = QToolButton()
        self.remove_button.setText("x")
        self.remove_button.setToolTip("Remove expression")
        self.remove_button.setFixedSize(24, 24)

        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(6)
        top.addWidget(self.enabled_box)
        top.addWidget(self.color_button)
        top.addWidget(self.expression_edit, 1)
        top.addWidget(self.remove_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 6, 7, 6)
        layout.setSpacing(3)
        layout.addLayout(top)
        layout.addWidget(self.math_preview)
        layout.addWidget(self.error_label)

        self.enabled_box.stateChanged.connect(self._sync_model)
        self.expression_edit.textChanged.connect(self._sync_model)
        self.color_button.clicked.connect(self._choose_color)
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.model.id))

    def _sync_model(self) -> None:
        self.model.enabled = self.enabled_box.isChecked()
        self.model.expression = self.expression_edit.text()
        self._update_math_preview()
        self.changed.emit()

    def set_error(self, message: str | None) -> None:
        self.model.error = message
        self.error_label.setText(message or "")

    def _choose_color(self) -> None:
        initial = QColor(self.model.color)
        chosen = QColorDialog.getColor(initial, self, "Choose expression color")
        if not chosen.isValid():
            return

        self.model.color = chosen.name()
        self._apply_color_style()
        self.changed.emit()

    def _apply_color_style(self) -> None:
        self.color_button.setStyleSheet(
            f"""
            QToolButton {{
                background: {self.model.color};
                border: 1px solid {DARK_THEME["button_border"]};
                border-radius: 6px;
                padding: 0;
            }}
            QToolButton:hover {{
                border: 1px solid {DARK_THEME["input_focus"]};
            }}
            """
        )

    def _update_math_preview(self) -> None:
        self.math_preview.setText(format_expression_html(self.expression_edit.text()))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1280, 800)

        self.rows: dict[str, ExpressionRow] = {}
        self.models: list[FunctionInput] = []
        self.compiled_functions: list[CompiledFunction] = []
        self.render_cache: dict[str, RenderCacheEntry] = {}
        self.compile_errors = 0
        self.manual_y_range = False

        self.expression_timer = QTimer(self)
        self.expression_timer.setSingleShot(True)
        self.expression_timer.setInterval(UPDATE_DEBOUNCE_MS)
        self.expression_timer.timeout.connect(self.rebuild_functions)

        self.range_timer = QTimer(self)
        self.range_timer.setSingleShot(True)
        self.range_timer.setInterval(UPDATE_DEBOUNCE_MS)
        self.range_timer.timeout.connect(self.apply_axis_range)

        self.viewport_timer = QTimer(self)
        self.viewport_timer.setSingleShot(True)
        self.viewport_timer.setInterval(VIEWPORT_RENDER_DEBOUNCE_MS)
        self.viewport_timer.timeout.connect(self.render_visible_range)

        self.graph = GraphWidget()
        self.graph.visible_range_changed.connect(self.schedule_viewport_render)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")

        self.x_min_edit = self._axis_edit(DEFAULT_X_MIN)
        self.x_max_edit = self._axis_edit(DEFAULT_X_MAX)
        self.y_min_edit = self._axis_edit(DEFAULT_Y_MIN)
        self.y_max_edit = self._axis_edit(DEFAULT_Y_MAX)

        self.expression_list = QVBoxLayout()
        self.expression_list.setContentsMargins(0, 0, 0, 0)
        self.expression_list.setSpacing(4)
        self.expression_list.addStretch(1)

        self._build_layout()
        self._apply_styles()

        for expr in DEFAULT_EXPRESSIONS:
            self.add_expression(expr)

        self.apply_axis_range()
        self.rebuild_functions()

    def _build_layout(self) -> None:
        central = QWidget()
        central.setObjectName("centralRoot")
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        self.setCentralWidget(central)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(350)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 14, 14, 14)
        sidebar_layout.setSpacing(12)

        title = QLabel(APP_TITLE)
        title.setObjectName("title")

        add_button = QPushButton("+ Add expression")
        add_button.clicked.connect(lambda: self.add_expression(""))

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setLayout(self.expression_list)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(scroll_content)

        axis_grid = QGridLayout()
        axis_grid.setHorizontalSpacing(8)
        axis_grid.setVerticalSpacing(8)
        axis_grid.addWidget(QLabel("x_min"), 0, 0)
        axis_grid.addWidget(self.x_min_edit, 0, 1)
        axis_grid.addWidget(QLabel("x_max"), 1, 0)
        axis_grid.addWidget(self.x_max_edit, 1, 1)
        axis_grid.addWidget(QLabel("y_min"), 2, 0)
        axis_grid.addWidget(self.y_min_edit, 2, 1)
        axis_grid.addWidget(QLabel("y_max"), 3, 0)
        axis_grid.addWidget(self.y_max_edit, 3, 1)

        apply_range = QPushButton("Apply range")
        apply_range.clicked.connect(self.apply_manual_axis_range)

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(add_button)
        sidebar_layout.addWidget(scroll, 1)
        sidebar_layout.addLayout(axis_grid)
        sidebar_layout.addWidget(apply_range)
        sidebar_layout.addWidget(self.status_label)

        graph_panel = QWidget()
        graph_panel.setObjectName("graphPanel")
        graph_layout = QVBoxLayout(graph_panel)
        graph_layout.setContentsMargins(1, 1, 1, 1)
        graph_layout.addWidget(self.graph)

        root.addWidget(sidebar)
        root.addWidget(graph_panel, 1)

        for edit in [self.x_min_edit, self.x_max_edit]:
            edit.textChanged.connect(self.schedule_range_update)
        for edit in [self.y_min_edit, self.y_max_edit]:
            edit.textChanged.connect(self.schedule_manual_y_range_update)

    def _apply_styles(self) -> None:
        self.setStyleSheet(app_stylesheet())

    def _axis_edit(self, value: float) -> QLineEdit:
        edit = QLineEdit(str(value).rstrip("0").rstrip("."))
        edit.setValidator(QDoubleValidator())
        edit.setAlignment(Qt.AlignRight)
        edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return edit

    def add_expression(self, expression: str) -> None:
        index = len(self.models)
        model = FunctionInput(
            expression=expression,
            color=PLOT_COLORS[index % len(PLOT_COLORS)],
        )
        row = ExpressionRow(model)
        row.changed.connect(self.schedule_expression_update)
        row.remove_requested.connect(self.remove_expression)

        self.models.append(model)
        self.rows[model.id] = row
        self.expression_list.insertWidget(self.expression_list.count() - 1, row)
        self.schedule_expression_update()

    def remove_expression(self, model_id: str) -> None:
        row = self.rows.pop(model_id, None)
        if row is not None:
            row.setParent(None)
            row.deleteLater()
        self.models = [model for model in self.models if model.id != model_id]
        self.schedule_expression_update()

    def schedule_expression_update(self) -> None:
        self.expression_timer.start()

    def schedule_range_update(self) -> None:
        self.range_timer.start()

    def schedule_manual_y_range_update(self) -> None:
        self.manual_y_range = True
        self.render_cache.clear()
        self.range_timer.start()

    def schedule_viewport_render(self) -> None:
        self.viewport_timer.start()

    def apply_manual_axis_range(self) -> None:
        self.manual_y_range = True
        self.render_cache.clear()
        self.apply_axis_range()

    def apply_axis_range(self) -> None:
        try:
            x_min, x_max, y_min, y_max = self._read_ranges()
        except ValueError as exc:
            self.status_label.setText(str(exc))
            self.status_label.setStyleSheet(f"color: {DARK_THEME['error']};")
            return

        if self.manual_y_range:
            self.graph.set_view_range(x_min, x_max, y_min, y_max, emit=False)
            self.render_visible_range(adjust_y=False)
        else:
            _, _, current_y_min, current_y_max = self.graph.visible_range()
            self.graph.set_view_range(x_min, x_max, current_y_min, current_y_max, emit=False)
            self.render_visible_range(adjust_y=True)

    def rebuild_functions(self) -> None:
        compiled_functions: list[CompiledFunction] = []
        errors = 0

        for model in self.models:
            row = self.rows[model.id]
            row.set_error(None)

            if not model.enabled or not model.expression.strip():
                continue

            try:
                expr = parse_expression(model.expression)
                func = build_function(expr)
                compiled_functions.append(
                    CompiledFunction(
                        id=model.id,
                        expression=model.expression,
                        color=model.color,
                        expr=expr,
                        func=func,
                    )
                )
            except ValueError as exc:
                errors += 1
                row.set_error(str(exc))

        self.compiled_functions = compiled_functions
        self.render_cache.clear()
        self.compile_errors = errors
        self.render_visible_range(adjust_y=not self.manual_y_range)

    def render_visible_range(self, adjust_y: bool = False) -> None:
        x_min, x_max, y_min, y_max = self.graph.visible_range()
        sample_count = adaptive_sample_count(
            pixel_width=self.graph.plot_pixel_width(),
            samples_per_pixel=SAMPLES_PER_PIXEL,
            min_points=MIN_SAMPLE_POINTS,
            max_points=MAX_SAMPLE_POINTS,
        )
        sample_x_min, sample_x_max = expanded_x_range(x_min, x_max, VIEWPORT_X_OVERSCAN_RATIO)
        expanded_sample_count = sample_count_for_range(
            visible_sample_count=sample_count,
            visible_x_min=x_min,
            visible_x_max=x_max,
            sample_x_min=sample_x_min,
            sample_x_max=sample_x_max,
            max_points=MAX_SAMPLE_POINTS,
        )

        series_list: list[GraphSeries] = []
        render_errors = 0
        recomputed_count = 0

        for compiled in self.compiled_functions:
            row = self.rows.get(compiled.id)
            segment_y_min = y_min if self.manual_y_range else None
            segment_y_max = y_max if self.manual_y_range else None
            try:
                cached = self.render_cache.get(compiled.id)
                if cached is None or not self._cache_covers_view(
                    cached,
                    x_min,
                    x_max,
                    segment_y_min,
                    segment_y_max,
                    expanded_sample_count,
                ):
                    segments = generate_segments(
                        compiled.func,
                        sample_x_min,
                        sample_x_max,
                        segment_y_min,
                        segment_y_max,
                        num_points=expanded_sample_count,
                    )
                    cached = RenderCacheEntry(
                        series=GraphSeries(
                            id=compiled.id,
                            expression=compiled.expression,
                            color=compiled.color,
                            segments=segments,
                        ),
                        x_min=sample_x_min,
                        x_max=sample_x_max,
                        y_min=segment_y_min,
                        y_max=segment_y_max,
                        sample_count=expanded_sample_count,
                    )
                    self.render_cache[compiled.id] = cached
                    recomputed_count += 1

                series_list.append(cached.series)
                if row is not None:
                    row.set_error(None)
            except ValueError as exc:
                render_errors += 1
                if row is not None:
                    row.set_error(str(exc))

        active_ids = {compiled.id for compiled in self.compiled_functions}
        for stale_id in set(self.render_cache) - active_ids:
            self.render_cache.pop(stale_id, None)

        if recomputed_count or self.graph.series_ids() != active_ids:
            self.graph.update_series(series_list)
        if adjust_y and not self.manual_y_range:
            self._apply_robust_auto_y_range(series_list, x_min, x_max)
        self._set_status(
            len(series_list),
            self.compile_errors + render_errors,
            sample_count,
            recomputed_count,
        )

    def update_graph(self) -> None:
        self.apply_axis_range()
        self.rebuild_functions()

    def _read_ranges(self) -> tuple[float, float, float, float]:
        try:
            x_min = float(self.x_min_edit.text())
            x_max = float(self.x_max_edit.text())
            y_min = float(self.y_min_edit.text())
            y_max = float(self.y_max_edit.text())
        except ValueError as exc:
            raise ValueError("Axis ranges must be valid numbers.") from exc

        if x_min >= x_max:
            raise ValueError("x_min must be smaller than x_max.")
        if y_min >= y_max:
            raise ValueError("y_min must be smaller than y_max.")

        return x_min, x_max, y_min, y_max

    def _apply_robust_auto_y_range(
        self,
        series_list: list[GraphSeries],
        x_min: float,
        x_max: float,
    ) -> None:
        all_segments = [
            segment
            for series in series_list
            for segment in series.segments
        ]
        limits = robust_y_limits(
            all_segments,
            visible_x_min=x_min,
            visible_x_max=x_max,
            percentile_low=AUTO_Y_PERCENTILE_LOW,
            percentile_high=AUTO_Y_PERCENTILE_HIGH,
            padding_ratio=AUTO_Y_PADDING_RATIO,
            min_span=AUTO_Y_MIN_SPAN,
        )
        if limits is None:
            return

        y_min, y_max = limits
        current_y_min, current_y_max = self.graph.visible_range()[2:]
        current_span = current_y_max - current_y_min
        next_span = y_max - y_min
        if current_span > 0:
            center_delta = abs(((current_y_min + current_y_max) / 2.0) - ((y_min + y_max) / 2.0))
            span_delta = abs(current_span - next_span)
            if center_delta < current_span * 0.03 and span_delta < current_span * 0.03:
                return

        self.graph.set_y_range(y_min, y_max, emit=False)
        self._set_axis_edit_text(self.y_min_edit, y_min)
        self._set_axis_edit_text(self.y_max_edit, y_max)

    def _set_axis_edit_text(self, edit: QLineEdit, value: float) -> None:
        edit.blockSignals(True)
        edit.setText(f"{value:.6g}")
        edit.blockSignals(False)

    def _cache_covers_view(
        self,
        cached: RenderCacheEntry,
        x_min: float,
        x_max: float,
        y_min: float | None,
        y_max: float | None,
        sample_count: int,
    ) -> bool:
        if x_min < cached.x_min or x_max > cached.x_max:
            return False
        if y_min != cached.y_min or y_max != cached.y_max:
            return False

        sample_delta = abs(sample_count - cached.sample_count)
        allowed_delta = max(1, int(cached.sample_count * RENDER_CACHE_SAMPLE_TOLERANCE))
        return sample_delta <= allowed_delta

    def _set_status(
        self,
        plotted_count: int,
        errors: int,
        sample_count: int | None = None,
        recomputed_count: int | None = None,
    ) -> None:
        sample_text = f" at {sample_count} samples" if sample_count else ""
        cache_text = ""
        if recomputed_count is not None:
            cache_text = f", refreshed {recomputed_count}" if recomputed_count else ", cache hit"
        if errors:
            self.status_label.setText(
                f"Plotted {plotted_count} expression(s){sample_text}{cache_text}, {errors} error(s)."
            )
            self.status_label.setStyleSheet(f"color: {DARK_THEME['error']};")
        else:
            self.status_label.setText(f"Plotted {plotted_count} expression(s){sample_text}{cache_text}.")
            self.status_label.setStyleSheet(f"color: {DARK_THEME['success']};")

    def closeEvent(self, event) -> None:
        self.expression_timer.stop()
        self.range_timer.stop()
        self.viewport_timer.stop()
        super().closeEvent(event)


def show_error(parent: QWidget, message: str) -> None:
    QMessageBox.critical(parent, APP_TITLE, message)
