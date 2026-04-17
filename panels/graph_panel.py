from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.placeholder = QLabel("그래프 영역")

        layout = QVBoxLayout()
        layout.addWidget(self.placeholder)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)