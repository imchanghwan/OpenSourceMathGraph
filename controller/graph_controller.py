from PySide6.QtGui import QColor
from ui.expression_list_panel import ExpressionListPanel
from ui.graph_panel import GraphPanel
from graph.graph_item import GraphItem

class GraphController:
    def __init__(self, graph_panel: GraphPanel, expression_panel: ExpressionListPanel):
        self.graph_panel = graph_panel
        self.expression_panel = expression_panel
        self.items: dict[str, GraphItem] = {}
        self._connect()
    
    def _connect(self):
        self.expression_panel.item_added.connect(self.on_item_added)
        self.expression_panel.item_removed.connect(self.on_item_removed)
        self.expression_panel.expression_changed.connect(self.on_expression_changed)
        self.expression_panel.color_changed.connect(self.on_color_changed)
        self.expression_panel.visible_changed.connect(self.on_visible_changed)

    def on_item_added(self, item_id: str):
        self.items[item_id] = GraphItem()

    def on_expression_changed(self, item_id: str, text: str):
        if item_id not in self.items:
            self.items[item_id] = GraphItem()

        self.items[item_id].update_from_text(text)

        if self.items[item_id].is_valid:
            self.graph_panel.update_plot(item_id, self.items[item_id])
        else:
            self.graph_panel.remove_plot(item_id)  # 잘못된 수식이면 그래프 제거

    def on_color_changed(self, item_id: str, color: QColor):
        self.items[item_id].color = color
        self.graph_panel.apply_style(item_id, self.items[item_id])

    def on_visible_changed(self, item_id: str, visible: bool):
        self.items[item_id].visible = visible
        self.graph_panel.set_visible(item_id, visible)

    def on_item_removed(self, item_id: str):
        self.graph_panel.remove_plot(item_id)
        del self.items[item_id]