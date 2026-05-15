import gradio as gr
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

# x 범위 안에서 수식들을 그려주는 함수
def draw_graph(items, x_min, x_max):
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.linspace(x_min, x_max, 800)

    for expr, color, visible in items:
        if not visible or not expr.strip():
            continue
        try:
            # numpy 함수(sin, cos 등)를 바로 쓸 수 있도록 네임스페이스 넘김
            y = eval(expr, {"x": x, **vars(np)})
            ax.plot(x, y, color=color, linewidth=2)
        except Exception:
            pass  # 잘못된 수식 무시

    ax.set_xlim(x_min, x_max)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig

def add_row(items):
    return items + [["", "#3b82f6", True]]

with gr.Blocks(title="그래프 계산기") as demo:
    # [수식, 색상, 표시여부] 리스트
    items = gr.State([["", "#3b82f6", True]])

    with gr.Row():
        # 왼쪽: 입력 패널
        with gr.Column(scale=1, min_width=280):
            gr.Markdown("## 수식 목록")

            with gr.Row():
                x_min = gr.Number(value=-10, label="x 최솟값")
                x_max = gr.Number(value=10,  label="x 최댓값")

            btn_add  = gr.Button("수식 추가", variant="primary")
            btn_draw = gr.Button("그래프 그리기")

            @gr.render(inputs=items)
            def render_list(current_items):
                for idx, (expr_val, color_val, vis_val) in enumerate(current_items):
                    with gr.Row():
                        clr = gr.ColorPicker(value=color_val, min_width=60, show_label=False, scale=1)
                        txt = gr.Textbox(value=expr_val, placeholder="y = f(x)  예: sin(x)", min_width=100, show_label=False, scale=4)
                        chk = gr.Checkbox(value=vis_val, label="표시", scale=1)
                        btn_del = gr.Button("삭제", min_width=50, scale=1)

                    # 클로저로 idx 캡처해서 items 업데이트
                    def make_updater(i):
                        def update(rows, c, e, v):
                            rows = [r[:] for r in rows]
                            rows[i] = [e, c, v]
                            return rows
                        return update

                    upd = make_updater(idx)
                    # txt는 blur(포커스 잃을 때)로 처리 - change로 하면 한 글자마다 재렌더돼서 입력 잠김
                    txt.blur(upd, [items, clr, txt, chk], items)
                    clr.change(upd, [items, clr, txt, chk], items)
                    chk.change(upd, [items, clr, txt, chk], items)
                    btn_del.click(
                        lambda rows, i=idx: [r for j, r in enumerate(rows) if j != i],
                        items, items
                    )

            btn_add.click(add_row, items, items)

        # 오른쪽: 그래프 영역
        with gr.Column(scale=2):
            gr.Markdown("## 그래프")
            plot = gr.Plot()
            btn_draw.click(draw_graph, [items, x_min, x_max], plot)

demo.launch()