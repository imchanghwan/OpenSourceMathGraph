from PySide6.QtWidgets import QCheckBox, QWidget, QHBoxLayout, QLineEdit, QPushButton, QColorDialog
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

class ExpressionItemWidget(QWidget):
    text_changed = Signal(str)          # text
    color_changed = Signal(QColor)      # color
    visible_changed = Signal(bool)      # visible
    delete_requested = Signal()

    def __init__(self):
        super().__init__()

        self.current_color = QColor("blue")  # 초기값

        self.color_button = QPushButton("●")
        self.input_edit = QLineEdit()
        self.delete_button = QPushButton("X")
        self.visible_checkbox = QCheckBox("표시")

        self.input_edit.setPlaceholderText("예: x**2 + 1")
        self.visible_checkbox.setChecked(True)

        layout = QHBoxLayout()
        layout.addWidget(self.color_button)
        layout.addWidget(self.input_edit)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.visible_checkbox)
        self.setLayout(layout)

        self.delete_button.clicked.connect(lambda: self.delete_requested.emit())
        self.input_edit.textChanged.connect(lambda text: self.text_changed.emit(text))
        self.color_button.clicked.connect(self.choose_color)
        self.visible_checkbox.stateChanged.connect(
            lambda state: self.visible_changed.emit(state == Qt.CheckState.Checked.value)
        )

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color)  # 현재 색상을 초기값으로
        if not color.isValid():
            return
        self.current_color = color
        self.color_changed.emit(color)