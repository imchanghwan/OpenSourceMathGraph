from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from core.parser import parse_expression
from core.graph_engine import build_graph_data
import numpy as np
import pyqtgraph as pg

class GraphItem:
    def __init__(self, curve=None, visible=True, 
                 color=QColor("blue"), 
                 width=2, line_style=Qt.PenStyle.SolidLine):
        # Model
        self.xs: np.ndarray = None
        self.ys: np.ndarray = None
        
        # View
        self.curve = curve
        self.visible = visible

        # Style
        self.color = color
        self.width = width
        self.line_style = line_style

    # 그래프 수식 변환
    def update_from_text(self, text: str):
        self.raw_text = text

        expr = parse_expression(text)
        self.expr = expr
        
        xs, ys = build_graph_data(expr)
        self.xs, self.ys = xs, ys

        self.render()

    # 그래프 렌더링
    def render(self, plot_widget: pg.PlotWidget, xs, ys):
        self.xs = xs
        self.ys = ys

        if self.curve is None:
            self.curve = plot_widget.plot(xs, ys)
            self.apply_style()
            self.set_visible(self.visible)
        else:
            self.curve.setData(xs, ys)

    # 그래프 Style 적용
    def apply_style(self):
        if self.curve is None:
            return
        pen = pg.mkPen(
            color=(self.color.red(), self.color.green(), self.color.blue()), 
            width=self.width, 
            style=self.line_style
        )
        self.curve.setPen(pen)

    def set_visible(self, visible: bool):
        self.visible = visible
        if self.curve:
            self.curve.setVisible(visible)

    def set_color(self, color: QColor):
        self.color = color
        if self.curve:
            self.apply_style()

    def set_width(self, width: int):
        self.width = width
        if self.curve:
            self.apply_style()

    def set_line_style(self, style: Qt.PenStyle):
        self.line_style = style
        if self.curve:
            self.apply_style()

    def remove(self, plot_widget: pg.PlotWidget):
        if self.curve:
            plot_widget.removeItem(self.curve)
            self.curve = None