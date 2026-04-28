from PySide6.QtGui import QColor
from core.parser import parse_expression
from core.graph_engine import build_graph_data
from core.graph_item import GraphItem
from widgets.expression_item_widget import ExpressionItemWidget
from errors.parse_error import ParseError
from panels.graph_panel import GraphPanel

class GraphController:
    def __init__(self, graph_panel: GraphPanel):
        self.graph_panel = graph_panel
        self.graph_dict: dict[str, GraphItem] = {}

    def _require_graph_item(self, item: ExpressionItemWidget) -> GraphItem:
        try:
            return self.graph_dict[id(item)]
        except KeyError:
            raise ValueError("GraphItem not found for given item")

    def create_graph(self, item: ExpressionItemWidget, text: str) -> GraphItem:
        item_id = id(item)

        graph_item = self.graph_dict.setdefault(item_id, GraphItem(item))
        graph_item.raw_text = text
        
        return graph_item
        

    def update_expression(self, item: ExpressionItemWidget, text: str):
        try:
            graph_item = self.create_graph(item, text)
            expr = parse_expression(text)
            graph_item.expr = expr
            
            graph_item.create_curve(self.graph_panel.plot_widget)
            xs, ys = build_graph_data(expr)
            graph_item.update_expression(xs, ys)
        except ParseError as e:
            self._handle_error(e)
            return
        except Exception as e:
            print(e)
            return
        
    def update_color(self, item: ExpressionItemWidget, color: QColor):
        graph_item = self._require_graph_item(item)
        graph_item.set_color(color)

    def update_visible(self, item: ExpressionItemWidget, visible: bool) -> None:
        graph_item = self._require_graph_item(item)
        graph_item.set_visible(visible)

    def remove(self, item: ExpressionItemWidget):
        pass

    def _handle_error(self, error):
        if isinstance(error, ParseError):
            # Handle parse error
            print(error);
            print(error.original)
            pass
        else:
            # Handle other errors
            pass