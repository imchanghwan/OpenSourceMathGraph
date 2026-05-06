import sys

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication
from utils.ui_loader import UILoader
from view.main_window import MainWindow
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    app = QApplication(sys.argv)

    app.setApplicationName("OpenSourceMathGraph")
    app.setStyle("Fusion")

    ui_loader = UILoader("ui/math_graph.ui")

    window = MainWindow(ui_loader.load())
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())