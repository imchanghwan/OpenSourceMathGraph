from core.parser import parse_expression
from core.graph_engine import build_graph_data
from core.graph_item import GraphItem
from widgets.expression_item_widget import ExpressionItemWidget

class GraphController:
    def __init__(self, graph_panel):
        self.graph_panel = graph_panel
        self.graph_dict = {}

    def create_graph(self, item: ExpressionItemWidget, text: str):
        graph_dict = None
        if item not in self.graph_dict:
            graph_dict = GraphItem(item)
            self.graph_dict[item] = graph_dict
        else:
            graph_dict = self.graph_dict[item]
        self.update_expression(item, text)

    def update_expression(self, item: ExpressionItemWidget, text: str):
        expr = parse_expression(text)
        if expr is None:
            self._handle_error(item)
            return

        xs, ys = build_graph_data(expr)
        graph_item = self._get_or_create(item)
        graph_item.update_expression(xs, ys)