from PySide6.QtWidgets import QCheckBox, QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Signal
class ExpressionItemWidget(QWidget):
    text_changed = Signal(object, str)
    color_changed = Signal(object, str)
    visible_changed = Signal(object, bool)

    def __init__(self):
        super().__init__()

        # 색상 표시, 수식 입력, 삭제 버튼
        self.color_button = QPushButton("●")
        self.input_edit = QLineEdit()
        self.delete_button = QPushButton("X")
        self.visible_checkbox = QCheckBox("표시")

        # 수식 입력 설정
        self.input_edit.setPlaceholderText("예: x**2 + 1")
        self.visible_checkbox.setChecked(True)

        # 레이아웃
        layout = QHBoxLayout()
        layout.addWidget(self.color_button)
        layout.addWidget(self.input_edit)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.visible_checkbox)

        self.setLayout(layout)

        # 콜백 연결
        self.delete_button.clicked.connect(self.delete_self)

        # 수식 입력 변경 시 text_changed 시그널 발신
        self.input_edit.textChanged.connect(
            lambda text: self.text_changed.emit(self, text)
        )
    
        # 색상 버튼과 가시성 체크박스 콜백 연결
        self.color_button.clicked.connect(
            lambda: self.color_changed.emit(self, "red")  # 예시로 빨간색 고정
        )

        # 가시성 체크박스 상태 변경 시 visible_changed 시그널 발신
        self.visible_checkbox.stateChanged.connect(
            lambda state: self.visible_changed.emit(self, bool(state))
        )

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()