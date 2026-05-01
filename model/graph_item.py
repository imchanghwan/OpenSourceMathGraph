from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from parser.parser import parse_expression
from graph.graph_engine import build_graph_data
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

    def update_from_text(self, text: str):
        self.raw_text = text

        try:
            self.expr = parse_expression(text)
            self.xs, self.ys = build_graph_data(self.expr)
            self.is_valid = True
        except ParseError:
            self.is_valid = False
        except BuildError:
            self.is_valid = False