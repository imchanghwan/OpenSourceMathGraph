import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.plot_widget = pg.PlotWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)