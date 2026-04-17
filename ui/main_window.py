from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from panels.expression_list_panel import ExpressionListPanel
from panels.graph_panel import GraphPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Math Graph")
        self.resize(1280, 720)

        # 중앙 위젯 (필수)
        central = QWidget()

        # 레이아웃
        layout = QHBoxLayout()

        self.expression_panel = ExpressionListPanel()
        self.graph_panel = GraphPanel()

        layout.addWidget(self.expression_panel)
        layout.addWidget(self.graph_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 3)

        central.setLayout(layout)
        
        self.setCentralWidget(central)