import flet as ft

def create_task_view(page: ft.Page) -> ft.Container:

    create_task_container = ft.Container(
        on_click=lambda _: page.go("/"),
        height=40,
        width=40,
        content=ft.Icon(
            name=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED
        )

    )

    return create_task_container