from PySide6.QtWidgets import QApplication, QMainWindow

def setup_screen(main_window: QMainWindow):
    screen = QApplication.primaryScreen()
    if screen is not None:
        geometry = screen.availableGeometry()
        main_window.setGeometry(geometry)
        main_window.showMaximized()