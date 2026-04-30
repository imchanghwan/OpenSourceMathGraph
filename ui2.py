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
    def __init__(self, formula, color, parent=None):
        super().__init__(parent)
        self.formula = formula
        self.graph_color = color


class Window(QMainWindow):
    graph_color_changed = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.default_graph_color = QColor("#000000")
        self.current_graph_color = QColor(self.default_graph_color)
        self.formula_rows = []
        self.selected_formula_row = None
        self.graph_widget = None

        self.setup_ui()
        self.btn_add_formula.clicked.connect(self.add_formula_row)
        self.btn_change_color.clicked.connect(self.change_current_color)

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
        self.left_layout.setSpacing(18)

        self.formula_input = QLineEdit(self.left_panel)
        self.formula_input.setObjectName("formula_input")
        self.formula_input.setMinimumHeight(54)
        self.formula_input.setPlaceholderText("수식을 입력하세요. 예: x**2")
        self.left_layout.addWidget(self.formula_input)

        self.formula_area = QWidget(self.left_panel)
        self.formulaRowsLayout = QVBoxLayout(self.formula_area)
        self.formulaRowsLayout.setContentsMargins(14, 0, 0, 0)
        self.formulaRowsLayout.setSpacing(10)
        self.formulaRowsLayout.addStretch(1)
        self.left_layout.addWidget(self.formula_area)
        self.left_layout.addStretch(1)

        self.bottom_controls = QWidget(self.left_panel)
        self.bottom_controls_layout = QVBoxLayout(self.bottom_controls)
        self.bottom_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_controls_layout.setSpacing(10)

        self.btn_add_formula = QPushButton("수식 추가", self.bottom_controls)
        self.btn_add_formula.setObjectName("btn_add_formula")
        self.btn_add_formula.setMinimumHeight(38)

        self.btn_change_color = QPushButton("색상 변경", self.bottom_controls)
        self.btn_change_color.setObjectName("btn_change_color")
        self.btn_change_color.setMinimumHeight(38)

        self.bottom_controls_layout.addWidget(self.btn_add_formula)
        self.bottom_controls_layout.addWidget(self.btn_change_color)
        self.left_layout.addWidget(self.bottom_controls)

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
            QLabel#graph_formula_label {
                color: #111111;
                padding-left: 4px;
            }
            QWidget#graph_row {
                background-color: transparent;
            }
            QWidget#graph_row[selected="true"] {
                background-color: #e8f3ff;
            }
            #graph_container,
            #graph_placeholder {
                background-color: #000000;
            }
            """
        )

    def add_formula_row(self):
        formula = self.formula_input.text().strip()
        if not formula:
            self.formula_input.setFocus()
            return

        color = QColor(self.current_graph_color)
        row_widget = GraphRowWidget(formula, color, self.formula_area)
        row_widget.setObjectName("graph_row")
        row_widget.setProperty("selected", False)
        row_widget.mousePressEvent = lambda event: self.select_formula_row(row_widget)

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        color_marker = QFrame(row_widget)
        color_marker.setObjectName("color_marker")
        color_marker.setFixedSize(16, 16)
        color_marker.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #777777;"
        )

        formula_label = QLabel(formula, row_widget)
        formula_label.setObjectName("graph_formula_label")
        formula_label.setMinimumHeight(30)
        formula_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        visible_check = QCheckBox("표시", row_widget)
        visible_check.setObjectName("visible_check")
        visible_check.setChecked(True)

        remove_button = QPushButton("X", row_widget)
        remove_button.setFixedSize(42, 30)
        remove_button.clicked.connect(lambda: self.remove_formula_row(row_widget))

        row_layout.addWidget(visible_check)
        row_layout.addWidget(color_marker)
        row_layout.addWidget(formula_label)
        row_layout.addWidget(remove_button)

        self.formulaRowsLayout.insertWidget(self.formulaRowsLayout.count() - 1, row_widget)
        row_data = {
            "widget": row_widget,
            "formula": formula,
            "formula_label": formula_label,
            "visible_check": visible_check,
            "color": color.name(),
            "color_marker": color_marker,
        }
        self.formula_rows.append(row_data)
        self.select_formula_row(row_widget)

        self.formula_input.clear()
        self.formula_input.setFocus()

    def select_formula_row(self, row_widget):
        self.selected_formula_row = row_widget

        for row in self.formula_rows:
            is_selected = row["widget"] is row_widget
            row["widget"].setProperty("selected", is_selected)
            row["widget"].style().unpolish(row["widget"])
            row["widget"].style().polish(row["widget"])

    def remove_formula_row(self, row_widget):
        if len(self.formula_rows) <= 1:
            return

        removed_row_was_selected = self.selected_formula_row is row_widget
        self.formula_rows = [
            row for row in self.formula_rows if row["widget"] is not row_widget
        ]
        row_widget.setParent(None)
        row_widget.deleteLater()

        if removed_row_was_selected:
            self.select_formula_row(self.formula_rows[-1]["widget"])

    def change_current_color(self):
        color = QColorDialog.getColor(self.current_graph_color, self, "그래프 색상")

        if not color.isValid():
            return

        self.current_graph_color = QColor(color)

        selected_index = self.selected_formula_row_index()
        if selected_index < 0:
            return

        row = self.formula_rows[selected_index]
        row["color"] = color.name()
        row["widget"].graph_color = QColor(color)
        row["color_marker"].setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #777777;"
        )
        self.graph_color_changed.emit(selected_index, color.name())

    def selected_formula_row_index(self):
        for index, row in enumerate(self.formula_rows):
            if row["widget"] is self.selected_formula_row:
                return index
        return -1

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
            formula = row["formula"].strip()
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
