from __future__ import annotations


DARK_THEME = {
    "window_bg": "#0d1117",
    "panel_bg": "#161b22",
    "panel_border": "#30363d",
    "row_bg": "#0f1623",
    "row_border": "#30363d",
    "input_bg": "#0d1117",
    "input_border": "#3f4b5a",
    "input_focus": "#58a6ff",
    "text": "#f0f6fc",
    "muted_text": "#c9d1d9",
    "placeholder": "#8b949e",
    "button_bg": "#21262d",
    "button_hover": "#30363d",
    "button_pressed": "#1f6feb",
    "button_border": "#8b949e",
    "error": "#ff7b72",
    "success": "#7ee787",
    "plot_bg": "#0b1018",
    "plot_axis": "#d0d7de",
    "plot_grid": "#30363d",
    "legend_bg": "#161b22",
}


def app_stylesheet() -> str:
    theme = DARK_THEME
    return f"""
    QMainWindow, QWidget#centralRoot {{
        background: {theme["window_bg"]};
        color: {theme["text"]};
    }}

    QFrame#sidebar {{
        background: {theme["panel_bg"]};
        border: 1px solid {theme["panel_border"]};
        border-radius: 8px;
    }}

    QWidget#graphPanel {{
        background: {theme["plot_bg"]};
        border: 1px solid {theme["panel_border"]};
        border-radius: 8px;
    }}

    QWidget#expressionRow {{
        background: {theme["row_bg"]};
        border: 1px solid {theme["row_border"]};
        border-radius: 6px;
    }}

    QWidget#expressionRow QLineEdit {{
        padding: 5px 7px;
    }}

    QWidget#expressionRow QCheckBox {{
        spacing: 5px;
    }}

    QLabel {{
        color: {theme["muted_text"]};
        background: transparent;
    }}

    QLabel#title {{
        color: {theme["text"]};
        font-size: 20px;
        font-weight: 700;
    }}

    QLabel#errorLabel {{
        color: {theme["error"]};
        font-size: 11px;
    }}

    QLabel#mathPreview {{
        color: {theme["text"]};
        font-size: 15px;
        padding: 1px 2px 0 30px;
    }}

    QLabel#statusLabel {{
        color: {theme["muted_text"]};
    }}

    QLineEdit {{
        color: {theme["text"]};
        background: {theme["input_bg"]};
        placeholder-text-color: {theme["placeholder"]};
        selection-color: {theme["text"]};
        selection-background-color: {theme["button_pressed"]};
        border: 1px solid {theme["input_border"]};
        border-radius: 6px;
        padding: 7px 8px;
    }}

    QLineEdit:focus {{
        border-color: {theme["input_focus"]};
    }}

    QLineEdit:disabled {{
        color: {theme["placeholder"]};
        background: #111722;
        border-color: {theme["panel_border"]};
    }}

    QPushButton, QToolButton {{
        color: {theme["text"]};
        background: {theme["button_bg"]};
        border: 1px solid {theme["button_border"]};
        border-radius: 6px;
        padding: 8px 10px;
    }}

    QPushButton:hover, QToolButton:hover {{
        background: {theme["button_hover"]};
        border-color: {theme["input_focus"]};
    }}

    QPushButton:pressed, QToolButton:pressed {{
        background: {theme["button_pressed"]};
        border-color: {theme["input_focus"]};
    }}

    QToolButton {{
        padding: 0;
        font-weight: 700;
    }}

    QCheckBox {{
        color: {theme["text"]};
        background: transparent;
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {theme["button_border"]};
        border-radius: 4px;
        background: {theme["input_bg"]};
    }}

    QCheckBox::indicator:checked {{
        background: {theme["button_pressed"]};
        border-color: {theme["input_focus"]};
    }}

    QScrollArea, QWidget#scrollContent {{
        background: transparent;
        border: 0;
    }}

    QScrollBar:vertical {{
        background: {theme["panel_bg"]};
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {theme["input_border"]};
        border-radius: 5px;
        min-height: 24px;
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """
