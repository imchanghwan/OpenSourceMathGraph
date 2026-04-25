from PySide6.QtCore import Qt
import numpy as np
import pyqtgraph as pg

class GraphItem:
    def __init__(self, item: object):
        self.item = item
        self.raw_text = ""
        self.expr = None
        self.curve = None
        self.visible = True
        self.color = "blue"
        self.width = 2
        self.line_style = Qt.PenStyle.SolidLine

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
        
        pen = pg.mkPen(color=self.color, width=self.width, style=self.line_style)
        self.curve.setPen(pen)

    def set_visible(self, visible: bool):
        self.visible = visible
        if self.curve is not None:
            self.curve.setVisible(visible)

    def set_color(self, color):
        self.color = color
        self.apply_style()

    def set_width(self, width: int):
        self.width = width
        self.apply_style()

    def set_line_style(self, style: Qt.PenStyle):
        self.line_style = style
        self.apply_style()

    def remove(self, plot_widget: pg.PlotWidget):
        if self.curve is not None:
            plot_widget.removeItem(self.curve)
            self.curve = None