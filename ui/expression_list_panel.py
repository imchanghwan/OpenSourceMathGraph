from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from ui.expression_item_widget import ExpressionItemWidget
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
import uuid

class ExpressionListPanel(QWidget):
    item_added = Signal(str)                    # id
    item_removed = Signal(str)                  # id
    expression_changed = Signal(str, str)       # (id, text)
    color_changed = Signal(str, QColor)         # (id, color)
    visible_changed = Signal(str, bool)         # (id, visible)

    def __init__(self):
        super().__init__()
        
        self.items: dict[str, ExpressionItemWidget] = {} # id -> widget

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
        item_id = str(uuid.uuid4())
        widget = ExpressionItemWidget()  # item_id 제거
        self.items[item_id] = widget
        
        self.layout.insertWidget(self.layout.count() - 1, widget)
        
        widget.text_changed.connect(lambda text, i=item_id: self.expression_changed.emit(i, text))
        widget.color_changed.connect(lambda color, i=item_id: self.color_changed.emit(i, color))
        widget.visible_changed.connect(lambda visible, i=item_id: self.visible_changed.emit(i, visible))
        widget.delete_requested.connect(lambda i=item_id: self.remove_expression_item(i))
        
        self.item_added.emit(item_id)
            
    def remove_expression_item(self, item_id: str):
        widget = self.items.pop(item_id)  # dict에서 제거
        self.layout.removeWidget(widget)
        widget.deleteLater()              # Qt 메모리 해제
        self.item_removed.emit(item_id)