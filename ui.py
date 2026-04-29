import sys
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QWidget,
)


UI_FILE = Path(__file__).with_name("ui.ui")
form_class = uic.loadUiType(str(UI_FILE))[0]


class Window(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setFont(QFont("Noto Sans KR", 10))
        self.default_graph_color = QColor("#1f77b4")
        self.formula_rows = []

        self.btn_add_formula.clicked.connect(self.add_formula_row)
        self.add_formula_row()

    def add_formula_row(self):
        row_number = len(self.formula_rows) + 1
        color = QColor(self.default_graph_color)

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        label = QLabel(f"수식 {row_number}")
        label.setMinimumWidth(54)

        line_edit = QLineEdit()
        line_edit.setMinimumHeight(40)
        line_edit.setPlaceholderText("수식을 입력하세요. 예: y=x, y=2*x, sin(x)")

        visible_check = QCheckBox("표시")
        visible_check.setChecked(True)

        color_button = QPushButton("선 색상 변경")
        color_button.setMinimumHeight(32)
        color_button.setProperty("graph_color", color.name())
        color_button.clicked.connect(lambda: self.change_row_color(color_button))
        self.apply_color_button_style(color_button, color)

        row_layout.addWidget(label)
        row_layout.addWidget(line_edit, 1)
        row_layout.addWidget(visible_check)
        row_layout.addWidget(color_button)

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

    def change_row_color(self, button):
        current_color = QColor(button.property("graph_color") or self.default_graph_color)
        color = QColorDialog.getColor(current_color, self, "그래프 선 색상")

        if not color.isValid():
            return

        button.setProperty("graph_color", color.name())
        self.apply_color_button_style(button, color)

    def apply_color_button_style(self, button, color):
        color_name = color.name()
        button.setStyleSheet(
            "QPushButton {"
            f" border: 1px solid {color_name};"
            f" color: {color_name};"
            " border-radius: 4px;"
            " padding: 4px 10px;"
            " background-color: #ffffff;"
            "}"
        )

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
    app.exec_()
