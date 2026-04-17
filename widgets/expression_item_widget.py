from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel

class ExpressionItemWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.color_label = QLabel("●")
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("예: x**2 + 1")
        
        self.delete_button = QPushButton("X")

        layout = QHBoxLayout()
        layout.addWidget(self.color_label)
        layout.addWidget(self.input_edit)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

        self.delete_button.clicked.connect(self.delete_self)

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()