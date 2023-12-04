import flet as ft

def create_task_view(page: ft.Page) -> ft.Container:


    task_create_page = ft.Row(
        controls=[
            ft.Container(
                width=600,
                padding=ft.padding.only(
                    top=10,
                    left=5,
                    right=5,
                    bottom=10
                ),
                content=ft.Column(
                    controls=[
                        ft.Container(
                            on_click=lambda _: page.go("/"),
                            content=ft.Icon(
                                name=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED,
                            ),
                        ),

                        ft.TextField(
                            label="My favorite color",
                            icon=ft.icons.FORMAT_SIZE,
                            hint_text="Type your favorite color",
                            helper_text="You can type only one color",
                            counter_text="0 symbols typed",
                            prefix_icon=ft.icons.COLOR_LENS,
                            suffix_text="...is your color",
                        )
                    ]
                )
            )
        ]
    )

    create_task_container = ft.Container(
        content=ft.Stack(
            controls=[
                task_create_page
            ]
        )

    )

    return create_task_container