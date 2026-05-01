from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from view.expression_list_panel import ExpressionListPanel
from view.graph_panel import GraphPanel
from controller.graph_controller import GraphController
from utils.screen_utils import setup_screen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Math Graph")
        # self.resize(1280, 720)
        setup_screen(self)

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

        self.graph_controller = GraphController(self.graph_panel, self.expression_panel)