import pymorphy3
import flet as ft

from database.db import fetch_categories

HEADER_COLOR_TEXT = "#FFFFFF"
WIDGET_COLOR = "#041965"
PINK_COLOR = "#eb06ff"


def main_window_view(page: ft.Page) -> ft.Container:
    # Сборка отображения категорий
    category_card = ft.Row(
        scroll="ALWAYS"
    )
    categories = fetch_categories()

    category_card.controls.append(
        ft.FloatingActionButton(
            icon=ft.icons.ADD,
            bgcolor=WIDGET_COLOR,
            on_click=lambda _: page.go("/create_task"),
            width=187,
            height=110
        ),
    )

    for index, category in enumerate(categories):
        category_name = categories[index]["name"]
        task_count = categories[index]["task_count"]

        morph = pymorphy3.MorphAnalyzer()
        word = morph.parse("задание")[0]
        task_word = word.make_agree_with_number(task_count).word

        category_card.controls.append(
            ft.Container(
                border_radius=20,
                bgcolor=WIDGET_COLOR,
                width=187,
                height=110,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text(value=f'{task_count} {task_word}'),
                        ft.Container(
                            width=160,
                            height=20,
                            content=ft.Text(
                                value=category_name,
                            ),
                        ),
                        ft.Container(
                            width=160,
                            height=5,
                            bgcolor="white12",
                            border_radius=20,
                            padding=ft.padding.only(
                                right=index * 50
                            ),
                            content=ft.Container(
                                bgcolor=PINK_COLOR
                            )
                        )
                    ]
                )
            ),
        )

    # Сборка отображения заданий
    task = ft.Column(
        height=400,
        scroll="ALWAYS"
    )

    for i in range(10):
        task.controls.append(
            ft.Container(
                height=80,
                width=600,
                bgcolor=WIDGET_COLOR,
                border_radius=20,

            ),
        )

    main_page = ft.Row(
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
                        ft.Text(
                            value="Категории:",
                            size=20
                        ),
                        ft.Container(
                            content=category_card
                        ),
                        ft.Container(height=20),
                        ft.Text(
                            value="Задания на сегодня:",
                            size=20

                        ),
                        ft.Stack(
                            controls=[
                                task,
                                ft.FloatingActionButton(
                                    bottom=2,
                                    right=10,
                                    icon=ft.icons.ADD,
                                    on_click=lambda _: page.go("/create_task")
                                )

                            ]
                        )
                    ]
                )
            ),
        ]
    )

    # Основной контейнер
    main_container = ft.Container(
        content=ft.Stack(
            controls=[
                main_page
            ]
        )
    )

    return main_container
