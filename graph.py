import flet as ft
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import time


def preprocess_expression(expr: str) -> str:
    expr = expr.strip()
    expr = expr.replace(" ", "")
    expr = expr.replace("^", "**")
    expr = expr.replace("²", "**2")
    expr = expr.replace("³", "**3")
    expr = re.sub(r"√\(", "sqrt(", expr)
    expr = re.sub(r"√([a-zA-Z0-9_.]+)", r"sqrt(\1)", expr)
    return expr


ALLOWED_NAMES = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "sqrt": np.sqrt,
    "log": np.log,
    "ln": np.log,
    "exp": np.exp,
    "abs": np.abs,
    "pi": np.pi,
    "e": np.e,
}


def evaluate_expression(expr: str, x: np.ndarray):
    local_dict = dict(ALLOWED_NAMES)
    local_dict["x"] = x
    return eval(expr, {"__builtins__": {}}, local_dict)


def create_plot_file(expr, x_min, x_max, y_min, y_max, filename):
    x = np.linspace(x_min, x_max, 1000)
    y = evaluate_expression(expr, x)

    plt.close("all")
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, label=f"y = {expr}")
    plt.axhline(0, color="black", linewidth=1)
    plt.axvline(0, color="black", linewidth=1)
    plt.grid(True)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.legend()
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("함수 그래프")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def main(page: ft.Page):
    page.title = "문자열 수식 그래프"
    page.window_width = 1000
    page.window_height = 800
    page.scroll = "auto"

    title = ft.Text("문자열 수식 그래프 프로그램", size=24, weight="bold")

    expr_input = ft.TextField(
        label="수식 입력",
        value="cos(x)",
        width=600
    )

    parsed_text = ft.Text("파싱 결과: ")
    status_text = ft.Text("", color="red")

    x_min = ft.TextField(label="x 최소", value="-10", width=100)
    x_max = ft.TextField(label="x 최대", value="10", width=100)
    y_min = ft.TextField(label="y 최소", value="-10", width=100)
    y_max = ft.TextField(label="y 최대", value="10", width=100)

    graph_img = ft.Image(
        src=None,
        width=800,
        height=500
    )

    current_image_path = {"path": None}

    def update_graph(e=None):
        try:
            raw_expr = expr_input.value
            parsed = preprocess_expression(raw_expr)

            xmin = float(x_min.value)
            xmax = float(x_max.value)
            ymin = float(y_min.value)
            ymax = float(y_max.value)

            if xmin >= xmax:
                raise ValueError("x 최소값은 x 최대값보다 작아야 합니다.")
            if ymin >= ymax:
                raise ValueError("y 최소값은 y 최대값보다 작아야 합니다.")

            test_x = np.linspace(xmin, xmax, 1000)
            evaluate_expression(parsed, test_x)

            # 파일명을 매번 새로 만들어서 이전 그래프 대신 새 그래프가 보이게 함
            new_filename = os.path.abspath(f"graph_{int(time.time() * 1000)}.png")
            create_plot_file(parsed, xmin, xmax, ymin, ymax, new_filename)

            # 이전 파일 삭제 시도
            if current_image_path["path"] and os.path.exists(current_image_path["path"]):
                try:
                    os.remove(current_image_path["path"])
                except:
                    pass

            current_image_path["path"] = new_filename

            # 이미지 교체
            graph_img.src = None
            page.update()

            graph_img.src = new_filename
            graph_img.visible = True

            parsed_text.value = f"파싱 결과: {parsed}"
            status_text.value = "새 그래프가 출력되었습니다."
            status_text.color = "green"

        except Exception as ex:
            status_text.value = f"오류: {ex}"
            status_text.color = "red"

        page.update()

    draw_btn = ft.ElevatedButton("그래프 그리기", on_click=update_graph)

    page.add(
        title,
        expr_input,
        parsed_text,
        status_text,
        ft.Row([x_min, x_max, y_min, y_max, draw_btn]),
        graph_img
    )


ft.app(target=main)