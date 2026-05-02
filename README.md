# OpenSourceMathGraph

**전체 구조 정리**

**아키텍처 흐름**

```
ExpressionItemWidget
    ↓ Signal (id 없이 데이터만)
ExpressionListPanel
    ↓ Signal (id + 데이터)
MainWindow
    ↓ connect
GraphController
    ↓ 계산 요청        ↓ 렌더링 요청
GraphItem          GraphPanel
(파싱 + 계산)      (curve 관리)
```

---

**각 클래스 책임**

| 클래스 | 책임 |
| --- | --- |
| `ExpressionItemWidget` | 입력 UI, id 모름, 데이터만 Signal 발신 |
| `ExpressionListPanel` | Widget 리스트 관리, id 생성, id 붙여서 Signal 중계 |
| `MainWindow` | Panel/Controller 생성, Signal 연결 |
| `GraphController` | id로 GraphItem 관리, 중재자 |
| `GraphItem` | 수식 파싱 + x/y 계산, UI 완전 무관 |
| `GraphPanel` | id 기반 curve 관리, 렌더링 |

### Signal 흐름 요약

```
# 추가
add_button.clicked → add_expression_item() → item_added(id) → on_item_added(id)

# 수식 변경
textChanged → text_changed(text) → expression_changed(id, text) → on_expression_changed(id, text)
                                                                  → update_from_text()
                                                                  → update_plot() or remove_plot()

# 색상 변경
color_button → color_changed(color) → color_changed(id, color) → on_color_changed(id, color)
                                                                 → apply_style()

# 가시성
checkbox → visible_changed(bool) → visible_changed(id, bool) → on_visible_changed(id, bool)
                                                               → set_visible()

# 삭제
delete_button → delete_requested() → remove_expression_item(id) → item_removed(id) → on_item_removed(id)
                                   → deleteLater()                                  → remove_plot()
```
