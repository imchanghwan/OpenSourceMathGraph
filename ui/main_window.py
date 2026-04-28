from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtGui import QColor

from core.graph_item import GraphItem
from core.parser import parse_expression
from core.graph_engine import build_graph_data
from panels.expression_list_panel import ExpressionListPanel
from panels.graph_panel import GraphPanel
from widgets.expression_item_widget import ExpressionItemWidget
from core.graph_controller import GraphController


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

        self.expression_panel.expression_changed.connect(self.graph_controller.update_expression)
        self.expression_panel.color_changed.connect(self.graph_controller.update_color)
        self.expression_panel.visible_changed.connect(self.graph_controller.update_visible)
        self.expression_panel.delete_requested.connect(self.remove_graph)

    def remove_graph(self, item: ExpressionItemWidget):
        if item in self.graph_dict:
            graph_item: GraphItem = self.graph_dict[item]
            graph_item.remove(self.graph_panel.plot_widget)
            del self.graph_dict[item]