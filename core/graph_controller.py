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

    def _get_or_create(self, item) -> GraphItem:
        item_id = id(item)

        graph_item = self.graph_dict.get(item_id)
        if graph_item is None:
            graph_item = GraphItem(item)
            self.graph_dict[item_id] = graph_item

        return graph_item

    def update_graph(self, item: ExpressionItemWidget, text: str):
        graph_item = self._get_or_create(item)
        graph_item.update_from_text(text)
        
    def update_color(self, item: ExpressionItemWidget, color: QColor):
        graph_item = self._get_or_create(item)
        graph_item.set_color(color)

    def update_visible(self, item: ExpressionItemWidget, visible: bool) -> None:
        graph_item = self._get_or_create(item)
        graph_item.set_visible(visible)

    def remove(self, item: ExpressionItemWidget):
        item_id = id(item)

        graph_item = self.graph_dict.pop(item_id, None)
        if graph_item is None:
            return

        graph_item.remove(self.graph_panel.plot_widget)
