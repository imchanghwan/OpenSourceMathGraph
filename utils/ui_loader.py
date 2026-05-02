from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader

class UILoader:
    def __init__(self, ui_file: str):
        self.ui_file = ui_file
        self.widget = None

    def load(self) -> QMainWindow:
        loader = QUiLoader()
        ui_file = QFile(self.ui_file)

        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError(f"UI 파일을 열 수 없습니다: {ui_file.errorString()}")

        ui = loader.load(ui_file)
        ui_file.close()

        if ui is None:
            raise RuntimeError("UI 로드 실패")
        
        return ui
