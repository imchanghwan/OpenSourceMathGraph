from PySide6.QtGui import QColor
from view.expression_list_panel import ExpressionListPanel
from view.graph_panel import GraphPanel
from model.graph_item import GraphItem
from PySide6.QtCore import QTimer

class GraphController:
    def __init__(self, graph_panel: GraphPanel, expression_panel: ExpressionListPanel):
        self.graph_panel = graph_panel
        self.expression_panel = expression_panel
        self.items: dict[str, GraphItem] = {}

        self.x_min, self.x_max = -10, 10
        self.y_min, self.y_max = -10, 10
        self._is_redrawing = False
        
        self._redraw_timer = QTimer()
        self._redraw_timer.setSingleShot(True)
        self._redraw_timer.setInterval(100)  # 100ms 후 재계산
        self._redraw_timer.timeout.connect(self._redraw_all)

        self._connect()
    
    def _connect(self):
        self.graph_panel.home_clicked.connect(self.reset_view)
        self.graph_panel.view_changed.connect(self.on_view_changed)
        self.expression_panel.item_added.connect(self.on_item_added)
        self.expression_panel.item_removed.connect(self.on_item_removed)
        self.expression_panel.expression_changed.connect(self.on_expression_changed)
        self.expression_panel.color_changed.connect(self.on_color_changed)
        self.expression_panel.visible_changed.connect(self.on_visible_changed)
    
    def on_view_changed(self, x_min: float, x_max: float, y_min: float, y_max: float):
        if self._is_redrawing:  # 재계산 중이면 무시
            return
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max
        self._redraw_timer.start()  # 타이머 리셋 

    def reset_view(self):
        # 초기 화면 범위로 복귀
        self.graph_panel.plot_widget.getViewBox().setRange(xRange=(-10, 10), yRange=(-10, 10))

    def _redraw_all(self):
        self._is_redrawing = True
        for item_id, item in self.items.items():
            if item.is_valid:
                item.update_from_text(item.raw_text, self.x_min, self.x_max, self.y_min, self.y_max)
                self.graph_panel.update_plot(item_id, item)
        self._is_redrawing = False

    def on_item_added(self, item_id: str):
        self.items[item_id] = GraphItem()

    def on_expression_changed(self, item_id: str, text: str):
        if item_id not in self.items:
            self.items[item_id] = GraphItem()
        self.items[item_id].update_from_text(text, self.x_min, self.x_max, self.y_min, self.y_max)

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
