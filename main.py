import flet as ft

def main(page: ft.Page):
    text = ft.Text("안녕")
    
    def click(e):
        text.value = "버튼 눌림"
        page.update()

    page.add(text, ft.ElevatedButton("클릭", on_click=click))

ft.run(main)