from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from widgets.expression_item_widget import ExpressionItemWidget

class ExpressionListPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        self.items = []

        self.layout = QVBoxLayout()
        self.add_button = QPushButton("수식 추가")

        self.layout.addWidget(self.add_button)
        self.layout.addStretch()  # 아래쪽 남는 공간 밀기
        
        self.setLayout(self.layout)

        self.add_button.clicked.connect(self.add_expression_item)

        self.add_expression_item()

    def add_expression_item(self):
        expression_item = ExpressionItemWidget()
        self.items.append(expression_item)
        
        self.layout.insertWidget(self.layout.count() - 1, expression_item)