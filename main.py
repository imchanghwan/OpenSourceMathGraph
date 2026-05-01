import sys

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication
from view.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)

    app.setApplicationName("OpenSourceMathGraph")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())