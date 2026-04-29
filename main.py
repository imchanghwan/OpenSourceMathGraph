from ui import Window


if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()
