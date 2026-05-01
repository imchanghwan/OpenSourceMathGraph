from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from ui.expression_list_panel import ExpressionListPanel
from ui.graph_panel import GraphPanel
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

        self.graph_controller = GraphController(self.graph_panel)

        self.expression_panel.item_added.connect(self.graph_controller.on_item_added)
        self.expression_panel.item_removed.connect(self.graph_controller.on_item_removed)
        self.expression_panel.expression_changed.connect(self.graph_controller.on_expression_changed)
        self.expression_panel.color_changed.connect(self.graph_controller.on_color_changed)
        self.expression_panel.visible_changed.connect(self.graph_controller.on_visible_changed)