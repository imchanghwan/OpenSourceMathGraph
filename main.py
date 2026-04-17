import flet as ft
import flet_charts as fch
import numpy as np
import plotly.graph_objects as go
import sympy as sp

x = sp.Symbol("x")


def parse_expression(expr_text: str):
    expr_text = expr_text.strip()

    if not expr_text:
        raise ValueError("수식을 입력하세요.")

    try:
        expr = sp.sympify(expr_text)
    except Exception as e:
        raise ValueError(f"수식 해석 실패: {e}")

    free_symbols = expr.free_symbols
    allowed_symbols = {x}
    if not free_symbols.issubset(allowed_symbols):
        raise ValueError("현재는 x 하나만 사용하는 식만 지원합니다.")

    return expr


def build_function(expr):
    try:
        func = sp.lambdify(x, expr, "numpy")
        return func
    except Exception as e:
        raise ValueError(f"함수 생성 실패: {e}")


def generate_xy(func, x_min: float, x_max: float, num_points: int = 1000):
    if x_min >= x_max:
        raise ValueError("x_min은 x_max보다 작아야 합니다.")

    xs = np.linspace(x_min, x_max, num_points)

    try:
        ys = func(xs)
    except Exception as e:
        raise ValueError(f"함수 계산 실패: {e}")

    if np.isscalar(ys):
        ys = np.full_like(xs, float(ys), dtype=float)

    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)

    if np.iscomplexobj(ys):
        ys = np.real(ys)

    mask = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[mask]
    ys = ys[mask]

    return xs, ys


def build_figure(xs, ys, expr_text: str, x_min: float, x_max: float, y_min: float, y_max: float):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name=expr_text,
        )
    )

    fig.update_layout(
        title=f"y = {expr_text}",
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
    )

    fig.update_xaxes(title_text="x", range=[x_min, x_max], zeroline=True)
    fig.update_yaxes(title_text="y", range=[y_min, y_max], zeroline=True)

    return fig


def main(page: ft.Page):
    page.title = "OpenSourceMathGraph"
    page.window_width = 1400
    page.window_height = 900
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO

    expr_input = ft.TextField(
        label="수식 입력",
        value="sin(x)",
        hint_text="예: x**2, sin(x), sqrt(x), 1/x",
        expand=True,
    )

    x_min_input = ft.TextField(label="x_min", value="-10", width=120)
    x_max_input = ft.TextField(label="x_max", value="10", width=120)
    y_min_input = ft.TextField(label="y_min", value="-10", width=120)
    y_max_input = ft.TextField(label="y_max", value="10", width=120)

    status_text = ft.Text(value="준비됨")

    initial_fig = go.Figure()
    initial_fig.update_layout(
        title="그래프 미리보기",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    chart = fch.PlotlyChart(
        figure=initial_fig,
        expand=True,
    )

    def draw_graph(e=None):
        try:
            expr_text = expr_input.value.strip()

            x_min = float(x_min_input.value)
            x_max = float(x_max_input.value)
            y_min = float(y_min_input.value)
            y_max = float(y_max_input.value)

            expr = parse_expression(expr_text)
            func = build_function(expr)
            xs, ys = generate_xy(func, x_min, x_max, num_points=2000)

            fig = build_figure(xs, ys, expr_text, x_min, x_max, y_min, y_max)

            chart.figure = fig
            status_text.value = f"성공: y = {expr_text}"
            status_text.color = ft.Colors.GREEN

        except Exception as ex:
            status_text.value = f"오류: {ex}"
            status_text.color = ft.Colors.RED

        page.update()

    draw_button = ft.ElevatedButton("그래프 그리기", on_click=draw_graph)

    page.add(
        ft.Column(
            controls=[
                ft.Text("OpenSourceMathGraph", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        expr_input,
                        draw_button,
                    ]
                ),
                ft.Row(
                    controls=[
                        x_min_input,
                        x_max_input,
                        y_min_input,
                        y_max_input,
                    ]
                ),
                status_text,
                ft.Container(
                    content=chart,
                    expand=True,
                    height=700,
                ),
            ],
            expand=True,
        )
    )

    draw_graph()


ft.run(main)