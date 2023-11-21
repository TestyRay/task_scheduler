from .main_window import main_window_view
from .tasks_window import create_task_view
from .categories_window import create_categories_view

import flet as ft


def MainWindow(page: ft.Page):

    # Установка заголовка окна
    page.title = "Планировщик задач"

    page.window_resizable = False
    page.window_maximized = True

    page.window_center()

    def route_change(route):
        # Очищаем представление
        page.views.clear()

        if page.route == "/":
            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        main_window_view(page=page)
                    ]
                ),
            )

        elif page.route == "/create_task":
            page.views.append(
                ft.View(
                    route="/create_task",
                    controls=[
                        create_task_view(page=page)
                    ]
                ),
            )

        elif page.route == "/create_category":
            page.views.append(
                ft.View(
                    route="/create_category",
                    controls=[
                        create_categories_view(page=page)
                    ]
                ),
            )

    page.on_route_change = route_change
    page.go(page.route)
