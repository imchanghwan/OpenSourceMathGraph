from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from widgets.expression_item_widget import ExpressionItemWidget
from PySide6.QtCore import Signal

class ExpressionListPanel(QWidget):
    expression_changed = Signal(object, str)
    color_changed = Signal(object, str)
    visible_changed = Signal(object, bool)
    def __init__(self):
        super().__init__()
        
        self.items: list[ExpressionItemWidget] = []

        # 레이아웃, 추가 버튼
        self.layout = QVBoxLayout()
        self.add_button = QPushButton("수식 추가")

        self.layout.addWidget(self.add_button)
        self.layout.addStretch()  # 아래쪽 남는 공간 밀기
        
        self.setLayout(self.layout)

        self.add_button.clicked.connect(self.add_expression_item)

        # 초기 수식 아이템 하나 추가
        self.add_expression_item()

    def add_expression_item(self):
        expression_item = ExpressionItemWidget()
        self.items.append(expression_item)
        
        self.layout.insertWidget(self.layout.count() - 1, expression_item)

        expression_item.text_changed.connect(self.on_expression_changed)
        expression_item.color_changed.connect(self.on_color_changed)
        expression_item.visible_changed.connect(self.on_visible_changed)

    # 수식이 변경 콜백
    def on_expression_changed(self, item: ExpressionItemWidget, text: str):
        self.expression_changed.emit(item, text)

    # 색상 변경 콜백
    def on_color_changed(self, item: ExpressionItemWidget, color: str):
        self.color_changed.emit(item, color)

    # 가시성 변경 콜백
    def on_visible_changed(self, item: ExpressionItemWidget, visible: bool):
        self.visible_changed.emit(item, visible)