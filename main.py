import sys
import numpy as np
import pyqtgraph as pg
import sympy as sp

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

from ui.main_window import MainWindow

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("OpenSourceMathGraph")
    
    window = MainWindow()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())