from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtGui import QColor

from graph.graph_item import GraphItem
from parser.parser import parse_expression
from graph.graph_engine import build_graph_data
from ui.expression_list_panel import ExpressionListPanel
from ui.graph_panel import GraphPanel
from ui.expression_item_widget import ExpressionItemWidget
from controller.graph_controller import GraphController


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

        self.graph_dict: dict[str, GraphItem] = {}

        layout.addWidget(self.expression_panel)
        layout.addWidget(self.graph_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 3)

        central.setLayout(layout)

        self.setCentralWidget(central)

        self.graph_controller = GraphController(self.graph_panel)

        self.expression_panel.expression_changed.connect(self.graph_controller.update_graph)
        self.expression_panel.color_changed.connect(self.graph_controller.update_color)
        self.expression_panel.visible_changed.connect(self.graph_controller.update_visible)
        self.expression_panel.delete_requested.connect(self.graph_controller.remove)