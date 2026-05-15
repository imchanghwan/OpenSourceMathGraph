import gradio as gr

def add_row(current_items):
    return current_items + [["", "#ff0000"]]

with gr.Blocks() as demo:
    # 1. 데이터 저장소 (수식, 색상)
    items = gr.State([["", "#ff0000"]])

    with gr.Row():
        # 왼쪽: 입력부
        with gr.Column(scale=1):
            btn_add = gr.Button("수식 추가")
            @gr.render(inputs=items)
            def render_list(current_items):
                for idx, item in enumerate(current_items):
                    with gr.Row():
                        gr.ColorPicker(value=item[1], scale=1, min_width=70, show_label=False)
                        gr.Textbox(value=item[0], placeholder="수식 입력", scale=3, min_width=70, show_label=False)
                        gr.Checkbox(value=True, label="표시", scale=1)
                        
                        btn_del = gr.Button("삭제", scale=1, min_width=70)
                        btn_del.click(lambda rows: [r for i, r in enumerate(rows) if i != idx], items, items)

            btn_add.click(add_row, items, items)

        # 오른쪽: 출력부
        with gr.Column(scale=2):
            gr.Plot(label="그래프")

demo.launch()