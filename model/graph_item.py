from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from model.parser import parse_expression
from model.graph_engine import build_graph_data
import numpy as np
from errors.parse_error import ParseError
from errors.build_error import BuildError

class GraphItem:
    def __init__(self, visible=True,
                 color=QColor("blue"),
                 width=2, line_style=Qt.PenStyle.SolidLine):
        self.xs: np.ndarray = None
        self.ys: np.ndarray = None
        self.raw_text: str = ""
        self.expr = None
        self.is_valid = False  # 유효한 수식인지 여부

        self.visible = visible
        self.color = color
        self.width = width
        self.line_style = line_style

    def update_from_text(self, text: str, x_min=-10, x_max=10, y_min=-10, y_max=10):
        self.raw_text = text

        try:
            self.expr = parse_expression(text)
            self.xs, self.ys = build_graph_data(self.expr, x_min, x_max, y_min, y_max)
            self.is_valid = True
        except ParseError as e:
            self.is_valid = False
            # raise ParseError(f"수식 파싱 실패: '{text}'", original=e)
        except BuildError as e:
            self.is_valid = False
            raise BuildError(f"그래프 데이터 생성 실패: '{text}'", original=e)