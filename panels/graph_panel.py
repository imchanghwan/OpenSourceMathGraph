import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.plot_widget = pg.PlotWidget()
        self.curve = self.plot_widget.plot([], [])

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def add_graph(self, xs, ys):
        self.curve.setData(xs, ys)