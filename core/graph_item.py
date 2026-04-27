from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import numpy as np
import pyqtgraph as pg

class GraphItem:
    def __init__(self, item: object, raw_text="", expr=None, 
                 curve=None, visible=True, color=QColor("blue"), width=2, 
                 line_style=Qt.PenStyle.SolidLine):
        self.item = item
        self.raw_text = raw_text
        self.expr = expr
        self.curve = curve
        self.visible = visible
        self.color = color
        self.width = width
        self.line_style = line_style

    # 그래프 아이템 생성
    def create_curve(self, plot_widget: pg.PlotWidget):
        if self.curve is None:
            self.curve = plot_widget.plot([], [])
            self.apply_style()
            self.set_visible(self.visible)

    # 그래프 데이터 업데이트
    def update_expression(self, xs, ys):
        if self.curve is None:
            return
        
        self.curve.setData(xs, ys)

    def apply_style(self):
        if self.curve is None:
            return
        pen = pg.mkPen(color=(self.color.red(), self.color.green(), self.color.blue()), 
                       width=self.width, 
                       style=self.line_style)
        self.curve.setPen(pen)

    def set_visible(self, visible: bool):
        self.visible = visible
        if self.curve is not None:
            self.curve.setVisible(visible)

    def set_color(self, color: QColor):
        self.color = color
        if self.curve is not None:
            self.apply_style()

    def set_width(self, width: int):
        self.width = width
        if self.curve is not None:
            self.apply_style()

    def set_line_style(self, style: Qt.PenStyle):
        self.line_style = style
        if self.curve is not None:
            self.apply_style()

    def remove(self, plot_widget: pg.PlotWidget):
        plot_widget.removeItem(self.curve)
        if self.curve is not None:
            self.curve = None