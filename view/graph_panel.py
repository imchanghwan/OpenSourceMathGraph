import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from graph.graph_item import GraphItem

class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.plot_widget = pg.PlotWidget()
        self.curves: dict[str, pg.PlotDataItem] = {}  # id → curve
        
        # 레이아웃 세팅
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_plot(self, item_id: str, item: GraphItem):
        if item_id not in self.curves:
            curve = self.plot_widget.plot(item.xs, item.ys)
            self.curves[item_id] = curve
            self.apply_style(item_id, item)
        else:
            self.curves[item_id].setData(item.xs, item.ys)

    def apply_style(self, item_id: str, item: GraphItem):
        curve = self.curves.get(item_id)
        if curve is None:
            return
        pen = pg.mkPen(
            color=(item.color.red(), item.color.green(), item.color.blue()),
            width=item.width,
            style=item.line_style
        )
        curve.setPen(pen)
        curve.setVisible(item.visible)

    def set_visible(self, item_id: str, visible: bool):
        if item_id in self.curves:
            self.curves[item_id].setVisible(visible)

    def remove_plot(self, item_id: str):
        if item_id in self.curves:
            self.plot_widget.removeItem(self.curves[item_id])
            del self.curves[item_id]