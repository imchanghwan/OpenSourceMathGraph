import sys

from app.qt_setup import prepare_qt_runtime

prepare_qt_runtime()

from PySide6.QtWidgets import QApplication

from app.ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("OpenSourceMathGraph")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
