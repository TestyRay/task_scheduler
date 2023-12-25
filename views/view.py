from .main_window import MainWindowView
from .tasks_window import (
    CreateTaskView,
    EditTaskView,
)
from .categories_window import (
    CreateCategoriesView,
    CategoriesView,
)

import flet as ft


def MainWindow(page: ft.Page):

    # Установка заголовка окна
    page.title = "Планировщик задач"

    page.window_resizable = False
    page.window_maximized = True

    page.window_center()

    def route_change(object_route):
        # Очищаем представление
        page.views.clear()

        if object_route.route == "/":
            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        MainWindowView(page=page)
                    ]
                ),
            )

        elif object_route.route == "/create_task":

            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        CreateTaskView(page=page)
                    ]
                ),
            )

        elif object_route.route == "/create_category":
            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        CreateCategoriesView(page=page)
                    ]
                ),
            )

        elif object_route.route.startswith("/category/"):
            category_id = object_route.route.split("/")[2]

            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        CategoriesView(
                            page=page,
                            category_id=category_id,
                        )
                    ]
                ),
            )

        elif object_route.route.startswith("/task/"):
            task_id = object_route.route.split("/")[2]

            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        EditTaskView(
                            page=page,
                            task_id=task_id,
                        )
                    ]
                ),
            )

    page.on_route_change = route_change
    page.go(page.route)
