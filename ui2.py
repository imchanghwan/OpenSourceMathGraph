import sys

from PyQt5.QtCore import Qt, pyqtSignal
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
    QVBoxLayout,
    QWidget,
)


class GraphRowWidget(QWidget):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.graph_color = color


class Window(QMainWindow):
    graph_formula_changed = pyqtSignal(int, str)
    graph_color_changed = pyqtSignal(int, str)
    graph_visibility_changed = pyqtSignal(int, bool)

    def __init__(self):
        super().__init__()

        self.default_graph_color = QColor("#000000")
        self.formula_rows = []
        self.selected_formula_row = None
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
        self.left_layout.setSpacing(14)

        self.btn_add_formula = QPushButton("수식 추가", self.left_panel)
        self.btn_add_formula.setObjectName("btn_add_formula")
        self.btn_add_formula.setMinimumHeight(46)
        self.left_layout.addWidget(self.btn_add_formula)

        self.formula_area = QWidget(self.left_panel)
        self.formulaRowsLayout = QVBoxLayout(self.formula_area)
        self.formulaRowsLayout.setContentsMargins(0, 0, 0, 0)
        self.formulaRowsLayout.setSpacing(8)
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
                font-size: 14px;
            }
            QPushButton#btn_add_formula {
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #e9e9e9;
            }
            QLineEdit {
                border: none;
                background-color: #ffffff;
                padding: 10px 12px;
                color: #222222;
                font-size: 18px;
            }
            QLineEdit:focus {
                border: none;
            }
            QCheckBox {
                color: #000000;
                spacing: 6px;
                font-size: 15px;
            }
            QWidget#graph_row {
                background-color: #ffffff;
                border-bottom: 1px solid #dddddd;
            }
            QWidget#graph_row[selected="true"] {
                border: 1px solid #2f73d9;
            }
            QLabel#row_number {
                background-color: #f1f1f1;
                color: #777777;
                padding-left: 4px;
            }
            QLabel#row_number[selected="true"] {
                background-color: #2f73d9;
                color: #ffffff;
            }
            #graph_container,
            #graph_placeholder {
                background-color: #000000;
            }
            """
        )

    def add_formula_row(self):
        color = QColor(self.default_graph_color)
        row_widget = GraphRowWidget(color, self.formula_area)
        row_widget.setObjectName("graph_row")
        row_widget.setProperty("selected", False)
        row_widget.mousePressEvent = lambda event: self.select_formula_row(row_widget)

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(8, 0, 8, 0)
        row_layout.setSpacing(10)

        row_number = QLabel(str(len(self.formula_rows) + 1), row_widget)
        row_number.setObjectName("row_number")
        row_number.setFixedSize(38, 38)
        row_number.setAlignment(Qt.AlignCenter)

        color_button = QPushButton("", row_widget)
        color_button.setObjectName("color_button")
        color_button.setFixedSize(38, 38)
        color_button.clicked.connect(lambda: self.change_row_color(row_widget))
        self.apply_color_button_style(color_button, color)

        line_edit = QLineEdit(row_widget)
        line_edit.setObjectName("formula_input")
        line_edit.setMinimumHeight(76)
        line_edit.setPlaceholderText("수식을 입력하세요. 예: x**2")
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.textChanged.connect(
            lambda text: self.emit_formula_changed(row_widget, text)
        )

        remove_button = QPushButton("X", row_widget)
        remove_button.setFixedSize(38, 38)
        remove_button.clicked.connect(lambda: self.remove_formula_row(row_widget))

        visible_check = QCheckBox("표시", row_widget)
        visible_check.setObjectName("visible_check")
        visible_check.setChecked(True)
        visible_check.setFixedSize(70, 76)
        visible_check.stateChanged.connect(
            lambda state: self.emit_visibility_changed(row_widget, state)
        )

        row_layout.addWidget(row_number)
        row_layout.addWidget(color_button)
        row_layout.addWidget(line_edit)
        row_layout.addWidget(remove_button)
        row_layout.addWidget(visible_check)

        self.formulaRowsLayout.insertWidget(self.formulaRowsLayout.count() - 1, row_widget)
        row_data = {
            "widget": row_widget,
            "row_number": row_number,
            "line_edit": line_edit,
            "visible_check": visible_check,
            "color": color.name(),
            "color_button": color_button,
        }
        self.formula_rows.append(row_data)
        self.select_formula_row(row_widget)

        line_edit.setFocus()

    def select_formula_row(self, row_widget):
        self.selected_formula_row = row_widget

        for row in self.formula_rows:
            is_selected = row["widget"] is row_widget
            row["widget"].setProperty("selected", is_selected)
            row["widget"].style().unpolish(row["widget"])
            row["widget"].style().polish(row["widget"])
            row["row_number"].setProperty("selected", is_selected)
            row["row_number"].style().unpolish(row["row_number"])
            row["row_number"].style().polish(row["row_number"])

    def remove_formula_row(self, row_widget):
        removed_row_was_selected = self.selected_formula_row is row_widget
        self.formula_rows = [
            row for row in self.formula_rows if row["widget"] is not row_widget
        ]
        row_widget.setParent(None)
        row_widget.deleteLater()
        self.renumber_formula_rows()

        if not self.formula_rows:
            self.selected_formula_row = None
            self.add_formula_row()
        elif removed_row_was_selected:
            self.select_formula_row(self.formula_rows[-1]["widget"])

    def change_row_color(self, row_widget):
        row_index = self.formula_row_index(row_widget)
        if row_index < 0:
            return

        current_color = QColor(self.formula_rows[row_index]["color"])
        color = QColorDialog.getColor(current_color, self, "그래프 색상")

        if not color.isValid():
            return

        row = self.formula_rows[row_index]
        row["color"] = color.name()
        row["widget"].graph_color = QColor(color)
        self.apply_color_button_style(row["color_button"], color)
        self.graph_color_changed.emit(row_index, color.name())

    def apply_color_button_style(self, button, color):
        button.setStyleSheet(
            "QPushButton {"
            " border: 1px solid #a8a8a8;"
            " border-radius: 4px;"
            f" background-color: {color.name()};"
            " padding: 0px;"
            "}"
            "QPushButton:hover { border: 2px solid #333333; }"
        )

    def emit_formula_changed(self, row_widget, text):
        row_index = self.formula_row_index(row_widget)
        if row_index >= 0:
            self.graph_formula_changed.emit(row_index, text.strip())

    def emit_visibility_changed(self, row_widget, state):
        row_index = self.formula_row_index(row_widget)
        if row_index >= 0:
            self.graph_visibility_changed.emit(row_index, state == Qt.Checked)

    def formula_row_index(self, row_widget):
        for index, row in enumerate(self.formula_rows):
            if row["widget"] is row_widget:
                return index
        return -1

    def renumber_formula_rows(self):
        for index, row in enumerate(self.formula_rows, start=1):
            row["row_number"].setText(str(index))

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
                    "color": row["color"],
                }
            )
        return settings


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
