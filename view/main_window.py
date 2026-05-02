from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from view.expression_list_panel import ExpressionListPanel
from view.graph_panel import GraphPanel
from controller.graph_controller import GraphController
from utils.screen_utils import setup_screen
from PySide6.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self, ui: QMainWindow):
        super().__init__()

        self.ui = ui
        self._setup_ui()

        setup_screen(self)

        central: QWidget = self.ui.centralWidget()
        self.setCentralWidget(central)

        add_button = central.findChild(QPushButton, "btn_add_expression")
        expression_area = central.findChild(QWidget, "expression_area")
        expression_layout: QVBoxLayout = expression_area.layout()

        graph_placeholder = central.findChild(QLabel, "graph_placeholder")
        graph_container = central.findChild(QWidget, "graph_container")
        graph_layout: QVBoxLayout = graph_container.layout()

        self.expression_panel = ExpressionListPanel(add_button, expression_layout)
        self.graph_panel = GraphPanel()

        graph_placeholder.hide()
        graph_layout.addWidget(self.graph_panel)

        self.graph_controller = GraphController(self.graph_panel, self.expression_panel)

    def _setup_ui(self):
        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.size())
        self.setMinimumSize(self.ui.minimumSize())
        self.setStyleSheet(self.ui.styleSheet())
        self.setFont(QFont("Noto Sans KR", 10))
