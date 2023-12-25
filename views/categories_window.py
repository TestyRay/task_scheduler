import flet as ft

from controllers import TaskScheduler
from database import add_category, fetch_categories, delete_category, update_category, fetch_tasks, change_task_status, \
    delete_task
from utils import show_alert_dialog, close_dialog_and_update, navigate_to_route
from views.main_window import WIDGET_COLOR, PINK_COLOR


class CreateCategoriesView(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.setup_ui()

    def setup_ui(self):
        # Инициализация элементов интерфейса
        self.init_elements()

        # Сборка представления создания категорий
        self.content = ft.Stack(
            controls=[
                self.container_title,
                self.container_back_button,
                self.row_create_category_form,
            ]
        )

    def init_elements(self):
        # Название раздела
        self.container_title = ft.Container(
            padding=ft.padding.only(
                top=200,
                left=5,
                right=5,
                bottom=10
            ),
            alignment=ft.alignment.center,
            content=ft.Text(
                value="Создать категорию:",
                size=30
            ),
        )

        # Текстовое поле для ввода названия категории
        self.text_field_name_category = ft.TextField(
            label="Введите название категории",
            hint_text="Например, Домашние дела, Работа, Учеба...",
            counter_text="Введено 0 из 50 возможных символов",
            on_change=self.on_text_changed,
        )

        # Кнопка назад
        self.container_back_button = ft.Container(
            padding=ft.padding.only(
                top=10,
                left=5,
                right=5,
                bottom=10
            ),
            on_click=lambda _: self.page.go("/"),
            content=ft.Icon(
                name=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED,
            ),
        )

        self.elevated_button_done = ft.ElevatedButton(
            text="Готово",
            on_click=self.button_clicked
        )

        # Формирование страницы создания категории
        self.row_create_category_form = self.create_category_form()

    def create_category_form(self):
        # Сборка представления создания категории
        return ft.Row(
            controls=[
                ft.Container(
                    width=700,
                    height=610,
                    padding=ft.padding.only(
                        top=250,
                        left=5,
                        right=5,
                        bottom=10
                    ),
                    content=ft.Column(
                        controls=[
                            self.text_field_name_category,
                            self.elevated_button_done,
                        ],

                    )
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def on_text_changed(self, e):
        # Обновление счетчика символов
        e.control.counter_text = (
            f"Введено {len(e.control.value)} из 50 возможных символов"
        )
        self.page.update()

    def button_clicked(self, e):

        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        category_name = self.text_field_name_category.value
        char_count = len(category_name)

        if char_count == 0:
            dlg = show_alert_dialog(
                page=self.page,
                title="Поле названия категории не должно быть пустым.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif char_count > 50:
            dlg = show_alert_dialog(
                page=self.page,
                title="Название категории не должно превышать 50 символов.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        else:
            result, error = add_category(category_name)

            if result:
                dlg = show_alert_dialog(
                    page=self.page,
                    title="Категория успешно создана!",
                    buttons=["Закрыть"],
                    funcs=[close_alert_dialog],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            else:
                dlg = show_alert_dialog(
                    page=self.page,
                    title=error,
                    buttons=["Закрыть"],
                    funcs=[close_alert_dialog],
                    alignment=ft.MainAxisAlignment.CENTER
                )


class CategoriesView(ft.Container):
    def __init__(self, page, category_id):
        super().__init__()
        self.page = page
        self.category_id = int(category_id)
        self.setup_ui()

    def update_ui(self):
        self.setup_ui()
        self.page.update()

    def setup_ui(self):
        # Инициализация элементов интерфейса
        self.init_elements()

        self.create_task_list()

        self.create_category_page()

        self.content = ft.Stack(
            controls=[
                self.category_page,
                self.container_back_button,
            ]
        )

    def init_elements(self):
        self.category = fetch_categories(category_id=self.category_id)[0]

        # Название раздела
        self.text_section_name = ft.Text(
            value=f"Категория \"{self.category['category_name']}\"",
            size=30
        )

        self.container_section_name = ft.Container(
            padding=ft.padding.only(
                top=30,
            ),
            alignment=ft.alignment.center,
            content=self.text_section_name
        )

        self.container_text_for_tasks = ft.Container(
            padding=ft.padding.only(
                top=0,
                bottom=0
            ),
            alignment=ft.alignment.center,
            content=ft.Text(
                value="Все задания:",
                size=20
            ),
        )

        # Текстовое поле для ввода названия категории
        self.text_field_name_category = ft.TextField(
            label="Введите название категории",
            hint_text="Например, Домашние дела, Работа, Учеба...",
            counter_text="Введено 0 из 50 возможных символов",
            on_change=self.on_text_changed,
        )

        self.alert_dialog_edit_category = ft.AlertDialog(
            modal=True,
            title=ft.Text("Введите название новой категории:"),
            content=ft.Container(
                height=100,
                width=20,
                content=ft.Column(
                    controls=[
                        self.text_field_name_category,
                    ]
                ),
            ),
            actions=[
                ft.TextButton("Назад", on_click=self.close_alert_dialog),
                ft.TextButton("Готово", on_click=self.edit_category),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.edit_button = ft.ElevatedButton(
            text="Редактировать категорию",
            on_click=self.show_alert_dialog,
        )
        self.delete_button = ft.ElevatedButton(
            text="Удалить категорию",
            on_click=self.show_bottom_sheet,
        )

        self.bottom_sheet_delete_category = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.Text(
                                    value="Вы действительно хотите удалить категорию?",
                                    size=18
                                )

                            ]
                        ),
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.ElevatedButton(
                                    text="Да",
                                    on_click=self.delete_category_alert_dialog
                                ),
                                ft.ElevatedButton(
                                    text="Нет",
                                    on_click=self.close_bottom_sheet
                                ),
                            ]
                        ),
                    ],
                    tight=True,
                ),
                padding=10,
            )
        )
        self.page.overlay.append(
            self.bottom_sheet_delete_category
        )

        # Кнопка назад
        self.container_back_button = ft.Container(
            padding=ft.padding.only(
                top=10,
                left=5,
                right=5,
                bottom=10
            ),
            on_click=lambda _: self.page.go("/"),
            content=ft.Icon(
                name=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED,
            ),
        )

        self.checked_check_box = False
        self.width_check_box = 2
        self.size_check_box = 30
        self.font_size_check_box = 25
        self.bgcolor_check_box_checked = "#183588"

        self.check_box_checked = ft.Container(
            width=self.size_check_box, height=self.size_check_box,
            border_radius=(self.size_check_box / 2) + 5,
            bgcolor=self.bgcolor_check_box_checked,
            content=ft.Icon(
                ft.icons.CHECK_ROUNDED,
                size=15,
            ),
        )

        self.check_box_unchecked = ft.Container(
            width=self.size_check_box, height=self.size_check_box,
            border_radius=(self.size_check_box / 2) + 5,
            bgcolor=None,
            border=ft.border.all(
                color=PINK_COLOR,
                width=self.width_check_box
            ),
            content=ft.Container(),
        )

        self.bottom_sheet_complete_task = self.build_bottom_sheet(
            text="Вы действительно хотите завершить эту задачу?",
            yes_func=self.complete_task,
            no_func=self.close_bottom_sheet_complete_task,
        )

        self.bottom_sheet_return_task = self.build_bottom_sheet(
            text="Вы действительно хотите вернуть эту задачу?",
            yes_func=self.return_task,
            no_func=self.close_bottom_sheet_return_task,
        )

        self.bottom_sheet_delete_task = self.build_bottom_sheet(
            text="Вы действительно хотите удалить эту задачу?",
            yes_func=self.delete_task,
            no_func=self.close_bottom_sheet_delete_task,
        )

        self.page.overlay.extend(
            [
                self.bottom_sheet_complete_task,
                self.bottom_sheet_return_task,
                self.bottom_sheet_delete_task,
            ]
        )

    def build_bottom_sheet(self, text, yes_func, no_func, text_size=18):
        return ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.Text(
                                    value=text,
                                    size=text_size
                                )

                            ]
                        ),
                        ft.Row(
                            alignment="CENTER",
                            controls=[
                                ft.ElevatedButton(
                                    text="Да",
                                    on_click=yes_func
                                ),
                                ft.ElevatedButton(
                                    text="Нет",
                                    on_click=no_func
                                ),
                            ]
                        ),
                    ],
                    tight=True,
                ),
                padding=10,
            )
        )

    def create_task_list(self):
        # Создание списка задач
        self.task_list = ft.Column(height=400, scroll="ALWAYS")
        tasks_data = self.category["tasks"]

        if tasks_data:
            self.add_tasks_display(data=tasks_data)
        else:
            self.add_no_tasks_display()

    def add_tasks_display(self, data):

        for task in data:
            task_id = task["task_id"]
            func_complete = lambda e, _id=task_id: self.show_bottom_sheet_complete_task(e, _id)
            func_return = lambda e, _id=task_id: self.show_bottom_sheet_return_task(e, _id)

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
                                                func_return
                                                if task["status_name"] == "Завершена"
                                                else func_complete
                                            ),
                                            content=(
                                                self.check_box_checked
                                                if task["status_name"] == "Завершена"
                                                else self.check_box_unchecked
                                            ),
                                        ),
                                        ft.Container(
                                            width=600,
                                            height=40,
                                            content=ft.Text(
                                                value=task["task_name"],
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
        self.task_list.controls.extend(
            [
                ft.Container(
                    height=220,
                    width=775,
                    padding=ft.padding.only(
                        top=50,
                        left=20,
                    ),
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
                    padding=ft.padding.only(
                        left=20,
                    ),
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
                    padding=ft.padding.only(
                        left=20,
                    ),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        value="Чтобы создать задачу, вернитесь в главное меню",
                        color=ft.colors.GREY,
                        size=18
                    ),
                ),
            ]
        )

    def create_category_page(self):
        self.category_page = ft.Row(
            controls=[
                ft.Container(
                    width=1280,
                    padding=ft.padding.only(
                        top=3,
                        left=250,
                        right=250,
                        bottom=10
                    ),
                    content=ft.Column(
                        controls=[
                            self.container_section_name,
                            ft.Container(height=10),
                            ft.Row(
                                alignment="CENTER",
                                controls=[
                                    self.edit_button,
                                    self.delete_button,
                                ]
                            ),
                            ft.Container(height=40),

                            self.container_text_for_tasks,
                            self.task_list

                        ]
                    )
                ),
            ]
        )

    def show_bottom_sheet(self, e):
        self.bottom_sheet_delete_category.open = True
        self.bottom_sheet_delete_category.update()

    def close_bottom_sheet(self, e):
        self.bottom_sheet_delete_category.open = False
        self.bottom_sheet_delete_category.update()

    def delete_category_alert_dialog(self, e):
        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        if any([
            self.category_id == 1,
            self.category["category_name"] == "Неопределенные",
        ]):
            dlg = show_alert_dialog(
                page=self.page,
                title="Данную категорию нельзя удалить.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )

        elif self.category["tasks"]:
            dlg = show_alert_dialog(
                page=self.page,
                title="Задачи, привязанные к категории, тоже удаляем?",
                buttons=["Да", "Нет", "Назад"],
                funcs=[self.delete_category_with_tasks, self.delete_category_without_tasks, close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        else:
            self.delete_category_with_tasks(e=None)

    def delete_category_with_tasks(self, e):
        delete_category(
            category_id=self.category_id,
            delete_tasks=True,
        )
        navigate_to_route(page=self.page, route="/")

    def delete_category_without_tasks(self, e):
        delete_category(category_id=self.category_id)
        navigate_to_route(page=self.page, route="/")

    def on_text_changed(self, e):
        # Обновление счетчика символов
        e.control.counter_text = (
            f"Введено {len(e.control.value)} из 50 возможных символов"
        )
        self.page.update()

    def show_alert_dialog(self, e):
        self.page.dialog = self.alert_dialog_edit_category
        self.alert_dialog_edit_category.open = True
        self.page.update()

    def close_alert_dialog(self, e):
        self.page.dialog = self.alert_dialog_edit_category
        self.alert_dialog_edit_category.open = False
        self.page.update()

    def edit_category(self, e):
        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        category_name = self.text_field_name_category.value
        char_count = len(category_name)

        if any([
            self.category_id == 1,
            self.category["category_name"] == "Неопределенные",
        ]):
            dlg = show_alert_dialog(
                page=self.page,
                title="Данную категорию нельзя переименовать.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif char_count == 0:
            dlg = show_alert_dialog(
                page=self.page,
                title="Поле названия категории не должно быть пустым.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif char_count > 50:
            dlg = show_alert_dialog(
                page=self.page,
                title="Название категории не должно превышать 50 символов.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif self.category["category_name"] == category_name:
            dlg = show_alert_dialog(
                page=self.page,
                title="Категория уже так названа.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        else:
            result, error = update_category(
                category_id=self.category_id,
                new_name=category_name
            )

            if result:
                self.setup_ui()
                self.page.update()

                dlg = show_alert_dialog(
                    page=self.page,
                    title="Категория успешно переименована!",
                    buttons=["Закрыть"],
                    funcs=[close_alert_dialog],
                    alignment=ft.MainAxisAlignment.CENTER
                )

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

    def show_bottom_sheet_return_task(self, e, task_id):
        self.current_task_id = task_id
        self.bottom_sheet_return_task.open = True
        self.bottom_sheet_return_task.update()

    def close_bottom_sheet_return_task(self, e):
        self.bottom_sheet_return_task.open = False
        self.bottom_sheet_return_task.update()

    def show_bottom_sheet_delete_task(self, e, task_id):
        self.current_task_id = task_id
        self.bottom_sheet_delete_task.open = True
        self.bottom_sheet_delete_task.update()

    def close_bottom_sheet_delete_task(self, e):
        self.bottom_sheet_delete_task.open = False
        self.bottom_sheet_delete_task.update()

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

    def return_task(self, e):

        self.bottom_sheet_return_task.open = False
        self.bottom_sheet_return_task.update()
        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        result, error = change_task_status(
            task_id=self.current_task_id,
            status_id=1,
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
