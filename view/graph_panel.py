import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt
from model.graph_item import GraphItem
from PySide6.QtCore import Signal

class GraphPanel(QWidget):
    view_changed = Signal(float, float, float, float) # x_min, x_max, y_min, y_max
    home_clicked = Signal()
    def __init__(self):
        super().__init__()
        self.plot_widget = pg.PlotWidget()
        self.home_button = QPushButton("Home")
        self.curves: dict[str, pg.PlotDataItem] = {}  # id → curve

        # 그래프 세팅
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')
        self.plot_widget.setBackground('#f5f5f5')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.plot_widget.getAxis('bottom').setPen('#888')
        self.plot_widget.getAxis('left').setPen('#888')

        # 레이아웃 세팅
        layout = QVBoxLayout()
        layout.addWidget(self.home_button)
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 자동 범위 조정 비활성화
        vb = self.plot_widget.getViewBox()
        vb.setAutoVisible(y=False)
        vb.enableAutoRange(enable=False)
        vb.setRange(xRange=(-10, 10), yRange=(-10, 10))  # 초기 범위

        self.home_button.clicked.connect(self.home_clicked.emit)
        vb.sigRangeChanged.connect(self.on_range_changed)

    def on_range_changed(self, viewbox, ranges):
        [[x_min, x_max], [y_min, y_max]] = ranges
        self.view_changed.emit(x_min, x_max, y_min, y_max)

    def update_plot(self, item_id: str, item: GraphItem):
        if item_id not in self.curves:
            curve = self.plot_widget.plot(item.xs, item.ys)
            self.curves[item_id] = curve
            self.apply_style(item_id, item)
        else:
            self.curves[item_id].setData(item.xs, item.ys, autoDownsample=False)

    def apply_style(self, item_id: str, item: GraphItem):
        curve = self.curves.get(item_id)
        if curve is None:
            return
        pen = pg.mkPen(
            color=(item.color.red(), item.color.green(), item.color.blue()),
            width=item.width,
            style=item.line_style,
            cap=Qt.RoundCap
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
