from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from core.graph_item import GraphItem
from core.parser import parse_expression
from core.graph_engine import build_graph_data
from panels.expression_list_panel import ExpressionListPanel
from panels.graph_panel import GraphPanel
from widgets.expression_item_widget import ExpressionItemWidget


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

        self.graph_dict: dict[object, GraphItem] = {}

        layout.addWidget(self.expression_panel)
        layout.addWidget(self.graph_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 3)

        central.setLayout(layout)

        self.setCentralWidget(central)

        self.expression_panel.expression_changed.connect(self.update_graph_expression)
        self.expression_panel.color_changed.connect(self.update_graph_color)
        self.expression_panel.visible_changed.connect(self.update_graph_visibility)
        self.expression_panel.delete_requested.connect(self.remove_graph)

    def update_graph_expression(self, item: ExpressionItemWidget, text: str):
        graph_item = None
        if item not in self.graph_dict:
            graph_item = GraphItem(item)
            graph_item.create_curve(self.graph_panel.plot_widget)
            self.graph_dict[item] = graph_item
        else:
            graph_item = self.graph_dict[item]

        graph_item.raw_text = text

        try:
            expr = parse_expression(text)
            graph_item.expr = expr

            xs, ys = build_graph_data(expr)
            graph_item.update_expression(xs, ys)
        except Exception as e:
            print(f"수식 파싱/그래프 생성 오류: {e}")

    def update_graph_color(self, item: ExpressionItemWidget, color: str):
        if item in self.graph_dict:
            graph_item = self.graph_dict[item]
            graph_item.set_color(color)

    def update_graph_visibility(self, item: ExpressionItemWidget, visible: bool):
        if item in self.graph_dict:
            graph_item = self.graph_dict[item]
            graph_item.set_visible(visible)

    def remove_graph(self, item: ExpressionItemWidget):
        if item in self.graph_dict:
            graph_item = self.graph_dict[item]
            graph_item.remove(self.graph_panel.plot_widget)
            del self.graph_dict[item]