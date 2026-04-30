import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.default_graph_color = QColor("#000000")
        self.formula_rows = []
        self.graph_widget = None

        self.setup_ui()
        self.btn_add_formula.clicked.connect(self.add_formula_row)
        self.add_formula_row()

    def setup_ui(self):
        self.setWindowTitle("Math Graph")
        self.resize(1920, 1125)
        self.setMinimumSize(1100, 650)
        self.setFont(QFont("Noto Sans KR", 10))

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.root_layout = QHBoxLayout(self.centralwidget)
        self.root_layout.setContentsMargins(28, 40, 28, 30)
        self.root_layout.setSpacing(36)

        self.left_panel = QWidget(self.centralwidget)
        self.left_panel.setFixedWidth(444)
        self.left_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(24)

        self.btn_add_formula = QPushButton("수식 추가", self.left_panel)
        self.btn_add_formula.setObjectName("btn_add_formula")
        self.btn_add_formula.setMinimumHeight(36)
        self.left_layout.addWidget(self.btn_add_formula)

        self.formula_area = QWidget(self.left_panel)
        self.formulaRowsLayout = QVBoxLayout(self.formula_area)
        self.formulaRowsLayout.setContentsMargins(14, 0, 0, 0)
        self.formulaRowsLayout.setSpacing(10)
        self.formulaRowsLayout.addStretch(1)
        self.left_layout.addWidget(self.formula_area)
        self.left_layout.addStretch(1)

        self.graph_container = QFrame(self.centralwidget)
        self.graph_container.setObjectName("graph_container")
        self.graph_container.setFrameShape(QFrame.NoFrame)
        self.graph_container.setMinimumSize(500, 400)
        self.graph_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_layout.setSpacing(0)

        self.graph_placeholder = QLabel("", self.graph_container)
        self.graph_placeholder.setObjectName("graph_placeholder")
        self.graph_placeholder.setAlignment(Qt.AlignCenter)
        self.graph_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graph_layout.addWidget(self.graph_placeholder)

        self.root_layout.addWidget(self.left_panel)
        self.root_layout.addWidget(self.graph_container, 1)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f3f3f3;
            }
            QPushButton {
                border: 1px solid #a8a8a8;
                border-radius: 3px;
                background-color: #f7f7f7;
                color: #000000;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #e9e9e9;
            }
            QLineEdit {
                border: 1px solid #9a9a9a;
                border-radius: 3px;
                background-color: #ffffff;
                padding: 3px 4px;
                color: #222222;
            }
            QLineEdit:focus {
                border: 1px solid #1a9cff;
            }
            QCheckBox {
                color: #000000;
                spacing: 6px;
            }
            #graph_container,
            #graph_placeholder {
                background-color: #000000;
            }
            """
        )

    def add_formula_row(self):
        row_widget = QWidget(self.formula_area)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        color_button = QPushButton(row_widget)
        color_button.setFixedSize(120, 36)
        color_button.setProperty("graph_color", self.default_graph_color.name())
        color_button.clicked.connect(lambda: self.change_row_color(color_button))
        self.apply_color_button_style(color_button, self.default_graph_color)

        line_edit = QLineEdit(row_widget)
        line_edit.setObjectName("formula_input")
        line_edit.setFixedSize(78, 36)
        line_edit.setPlaceholderText("예: x**2")

        remove_button = QPushButton("X", row_widget)
        remove_button.setFixedSize(120, 36)
        remove_button.clicked.connect(lambda: self.remove_formula_row(row_widget))

        visible_check = QCheckBox("표시", row_widget)
        visible_check.setObjectName("visible_check")
        visible_check.setChecked(True)

        row_layout.addWidget(color_button)
        row_layout.addWidget(line_edit)
        row_layout.addWidget(remove_button)
        row_layout.addWidget(visible_check)
        row_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.formulaRowsLayout.insertWidget(self.formulaRowsLayout.count() - 1, row_widget)
        self.formula_rows.append(
            {
                "widget": row_widget,
                "line_edit": line_edit,
                "visible_check": visible_check,
                "color_button": color_button,
            }
        )
        line_edit.setFocus()

    def remove_formula_row(self, row_widget):
        if len(self.formula_rows) <= 1:
            return

        self.formula_rows = [
            row for row in self.formula_rows if row["widget"] is not row_widget
        ]
        row_widget.setParent(None)
        row_widget.deleteLater()

    def change_row_color(self, button):
        current_color = QColor(button.property("graph_color") or self.default_graph_color)
        color = QColorDialog.getColor(current_color, self, "그래프 색상")

        if not color.isValid():
            return

        button.setProperty("graph_color", color.name())
        self.apply_color_button_style(button, color)

    def apply_color_button_style(self, button, color):
        color_name = color.name()
        button.setText("●")
        button.setStyleSheet(
            "QPushButton {"
            " border: 1px solid #b2b2b2;"
            " border-radius: 3px;"
            " background-color: #f7f7f7;"
            f" color: {color_name};"
            " font-size: 24px;"
            " padding-bottom: 3px;"
            "}"
            "QPushButton:hover { background-color: #ffffff; }"
        )

    def set_graph_widget(self, widget):
        if self.graph_widget is not None:
            self.graph_layout.removeWidget(self.graph_widget)
            self.graph_widget.setParent(None)

        self.graph_placeholder.hide()
        self.graph_widget = widget
        self.graph_widget.setParent(self.graph_container)
        self.graph_layout.addWidget(self.graph_widget)

    def formula_settings(self):
        settings = []
        for row in self.formula_rows:
            formula = row["line_edit"].text().strip()
            if not formula:
                continue

            settings.append(
                {
                    "formula": formula,
                    "visible": row["visible_check"].isChecked(),
                    "color": row["color_button"].property("graph_color"),
                }
            )
        return settings


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
