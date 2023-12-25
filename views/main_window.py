import flet as ft

from controllers import TaskScheduler
from database import (
    fetch_categories,
    fetch_tasks, change_task_status, delete_task,
)
from utils import (
    pluralize_word,
    show_alert_dialog,
    close_dialog_and_update,
)

WIDGET_COLOR = "#041965"
PINK_COLOR = "#eb06ff"


class MainWindowView(ft.Container):

    def __init__(self, page):
        super().__init__()
        self.page = page
        self.setup_ui()

    def update_ui(self):
        self.setup_ui()
        self.page.update()

    def setup_ui(self):
        # Создаем элементы интерфейса
        self.init_elements()

        self.create_category_card()
        self.create_task_list()

        # Основная страница
        self.create_main_page()

        # Устанавливаем содержимое контейнера
        self.content = ft.Stack(controls=[self.main_page])


    def init_elements(self):
        self.checked_check_box = False
        self.width_check_box = 2
        self.size_check_box = 30
        self.font_size_check_box = 25
        self.bgcolor_check_box_checked = "#183588"

        self.check_box = ft.Container(
            width=self.size_check_box, height=self.size_check_box,
            border_radius=(self.size_check_box / 2) + 5,
            bgcolor=None,
            border=ft.border.all(
                color=PINK_COLOR,
                width=self.width_check_box
            ),
            content=ft.Container(),
        )

        self.bottom_sheet_complete_task = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.Text(
                                    value="Вы действительно хотите завершить эту задачу?",
                                    size=18
                                )

                            ]
                        ),
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.ElevatedButton(
                                    text="Да",
                                    on_click=self.complete_task
                                ),
                                ft.ElevatedButton(
                                    text="Нет",
                                    on_click=self.close_bottom_sheet_complete_task
                                ),
                            ]
                        ),
                    ],
                    tight=True,
                ),
                padding=10,
            )
        )
        self.bottom_sheet_delete_task = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.Text(
                                    value="Вы действительно хотите удалить эту задачу?",
                                    size=18
                                )

                            ]
                        ),
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.ElevatedButton(
                                    text="Да",
                                    on_click=self.delete_task
                                ),
                                ft.ElevatedButton(
                                    text="Нет",
                                    on_click=self.close_bottom_sheet_delete_task
                                ),
                            ]
                        ),
                    ],
                    tight=True,
                ),
                padding=10,
            )
        )

        self.page.overlay.extend(
            [
                self.bottom_sheet_complete_task,
                self.bottom_sheet_delete_task,
            ]
        )

    def create_category_card(self):
        # Создание карточки категорий
        self.category_card = ft.Row(scroll="ALWAYS")

        categories = fetch_categories()

        self.category_card.controls.append(
            ft.FloatingActionButton(
                icon=ft.icons.ADD,
                bgcolor=WIDGET_COLOR,
                on_click=lambda _: self.page.go("/create_category"),
                width=187,
                height=110
            ),
        )

        for index, category in enumerate(categories):
            category_id = category["category_id"]
            category_name = category["category_name"]

            task_count = len(category["tasks"])
            task_word = pluralize_word(word="задание", number=task_count)

            self.category_card.controls.append(
                ft.Container(
                    border_radius=20,
                    bgcolor=WIDGET_COLOR,
                    width=187,
                    height=110,
                    padding=20,
                    on_click=lambda _, _id=category_id: self.page.go(f'/category/{_id}'),
                    content=ft.Column(
                        controls=[
                            ft.Text(value=f'{task_count} {task_word}'),
                            ft.Container(
                                width=160, height=20,
                                content=ft.Text(value=category_name)
                            ),
                            ft.Container(
                                width=160,
                                height=5,
                                bgcolor="white12",
                                border_radius=20,
                                # padding=ft.padding.only(right=index * 50),
                                content=ft.Container(bgcolor=PINK_COLOR)
                            )
                        ]
                    )
                ),
            )

    def create_task_list(self):
        # Создание списка задач
        self.task_list = ft.Column(height=400, scroll="ALWAYS")
        tasks_data = fetch_tasks(include_completed=False)

        if tasks_data:
            self.add_tasks_display(data=tasks_data)
        else:
            self.add_no_tasks_display()

    def add_tasks_display(self, data):

        for task in data:
            task_id = task["id"]
            self.task_list.controls.append(
                ft.Container(
                    # on_click=lambda _, _id=task_id: self.page.go(f'/task/{_id}'),
                    height=80,
                    width=775,
                    bgcolor=WIDGET_COLOR,
                    border_radius=20,
                    padding=ft.padding.only(
                        top=20, left=20,
                        right=20, bottom=20
                    ),
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Container(
                                            on_click=(
                                                lambda e, _id=task_id:
                                                self.show_bottom_sheet_complete_task(e, _id)
                                            ),
                                            content=self.check_box,
                                        ),
                                        ft.Container(
                                            width=600,
                                            height=40,
                                            content=ft.Text(
                                                value=task["name"],
                                                font_family='poppins',
                                                size=self.font_size_check_box,
                                                weight=ft.FontWeight.W_300,
                                            )
                                        ),
                                        ft.Container(
                                            on_click=(
                                                lambda _, _id=task_id:
                                                self.page.go(f'/task/{_id}')
                                            ),
                                            content=ft.Icon(
                                                name=ft.icons.EDIT_OUTLINED,
                                                size=40,
                                                color=PINK_COLOR,
                                            )
                                        ),
                                        ft.Container(
                                            on_click=(
                                                lambda e, _id=task_id:
                                                self.show_bottom_sheet_delete_task(e, _id)
                                            ),
                                            content=ft.Icon(
                                                name=ft.icons.RESTORE_FROM_TRASH_SHARP,
                                                size=40,
                                                color=ft.colors.RED_500,
                                            )
                                        ),

                                    ]
                                )
                            )
                        ]
                    )
                ),
            )

    def add_no_tasks_display(self):
        # Добавление отображения для пустого списка задач
        self.task_list.controls.extend([
            ft.Container(
                height=220,
                width=775,
                padding=ft.padding.only(top=70),
                alignment=ft.alignment.center,
                content=ft.Icon(
                    name=ft.icons.STAR_BORDER_ROUNDED,
                    color=ft.colors.GREY,
                    size=180
                ),
            ),
            ft.Container(
                height=65,
                width=775,
                alignment=ft.alignment.center,
                content=ft.Text(
                    value="Нет задач",
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY,
                    size=28
                ),
            ),
            ft.Container(
                height=50,
                width=775,
                alignment=ft.alignment.center,
                content=ft.Text(
                    value="Нажмите кнопку +, чтобы создать задачу",
                    color=ft.colors.GREY,
                    size=18
                ),
            ),
        ])

    def create_main_page(self):
        self.main_page = ft.Row(
            controls=[
                ft.Container(
                    width=1280,
                    padding=ft.padding.only(top=3, left=250, right=250, bottom=10),
                    content=ft.Column(
                        controls=[
                            ft.Text(value="Категории:", size=20),
                            ft.Container(content=self.category_card),
                            ft.Container(height=25),
                            ft.Text(value="Задания на сегодня:", size=20),
                            ft.Stack(
                                controls=[
                                    self.task_list,
                                    ft.FloatingActionButton(
                                        bottom=2,
                                        right=10,
                                        icon=ft.icons.ADD,
                                        on_click=lambda _: self.page.go("/create_task")
                                    )
                                ]
                            ),
                        ]
                    )
                ),
            ]
        )

    def complete_task(self, e):
        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        result, error = change_task_status(
            task_id=self.current_task_id,
            status_id=3,
        )

        if result:
            task_scheduler = TaskScheduler()
            task_scheduler.clear_scheduled_task(
                self.current_task_id
            )

            self.bottom_sheet_complete_task.open = False
            self.bottom_sheet_complete_task.update()

            self.update_ui()


        else:
            dlg = show_alert_dialog(
                page=self.page,
                title=error,
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )

    def show_bottom_sheet_complete_task(self, e, task_id):
        self.current_task_id = task_id
        self.bottom_sheet_complete_task.open = True
        self.bottom_sheet_complete_task.update()

    def close_bottom_sheet_complete_task(self, e):
        self.bottom_sheet_complete_task.open = False
        self.bottom_sheet_complete_task.update()

    def show_bottom_sheet_delete_task(self, e, task_id):
        self.current_task_id = task_id
        self.bottom_sheet_delete_task.open = True
        self.bottom_sheet_delete_task.update()

    def close_bottom_sheet_delete_task(self, e):
        self.bottom_sheet_delete_task.open = False
        self.bottom_sheet_delete_task.update()

    def delete_task(self, e):
        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        result, error = delete_task(
            task_id=self.current_task_id,
        )
        if result:
            self.update_ui()
            dlg = show_alert_dialog(
                page=self.page,
                title="Задача успешно удалена!",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
            task_scheduler = TaskScheduler()
            task_scheduler.clear_scheduled_task(
                self.current_task_id
            )

        else:
            dlg = show_alert_dialog(
                page=self.page,
                title=error,
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )