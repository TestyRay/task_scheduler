import datetime

import flet as ft

from controllers import TaskScheduler
from database import add_task, fetch_categories, fetch_tasks, update_task, fetch_statuses
from utils import (
    show_alert_dialog,
    send_notification,
    close_dialog_and_update,
    navigate_to_route,
)


class CreateTaskView(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.current_date = datetime.datetime.now().date()
        self.current_time = datetime.datetime.now().time()

        self.page = page
        self.setup_ui()

    def setup_ui(self):
        # Инициализация элементов интерфейса
        self.init_elements()

        # Собираем весь интерфейс
        self.content = ft.Stack(
            controls=[
                self.container_back_button,
                self.row_task_form,
            ]
        )

    def init_elements(self):
        # Название раздела
        self.container_section_name = ft.Container(
            alignment=ft.alignment.center,
            content=ft.Text(
                value="Создать задачу:",
                size=30
            ),
        )

        # Input-поля
        self.text_field_name_task = ft.TextField(
            label="Введите название",
            hint_text="Например, Подготовка к экзаменам..",
            counter_text="Введено 0 из 50 возможных символов",
            # Добавляем обработчик события изменения текста
            on_change=self.on_text_changed,
            value="",
        )
        self.text_field_description_task = ft.TextField(
            label="Введите описание",
            multiline=True,
            min_lines=1,
            max_lines=10,
            value="",
        )

        # Input-поля, отображающие дату и время
        self.text_field_date = ft.TextField(
            label="Дата",
            disabled=True,
            value=self.current_date.strftime('%m/%d/%Y'),
        )
        self.text_field_time = ft.TextField(
            label="Время",
            disabled=True,
            value=self.current_time.strftime('%H:%M'),
        )

        # Объекты выбора даты и времени
        self.date_picker = ft.DatePicker(
            on_change=self.on_date_changed,
            cancel_text="Отмена",
            confirm_text="Ок",
            error_format_text="Недопустимый формат даты",
            error_invalid_text="Дата вне допустимого диапазона",
            field_label_text="Введите дату",
            help_text="Выберите дату",
            switch_to_calendar_icon="Ввести вручную",
            switch_to_input_icon="Вернуться к календарю",
            first_date=self.current_date,
            value=self.current_date,
        )
        self.time_picker = ft.TimePicker(
            on_change=self.on_time_changed,
            cancel_text="Отмена",
            confirm_text="Ок",
            error_invalid_text="Недопустимый формат времени",
            hour_label_text="Часы",
            minute_label_text="Минуты",
            help_text="Введите время",
            value=self.current_time
        )
        self.page.overlay.extend(
            [self.date_picker, self.time_picker]
        )

        self.container_date_picker = ft.Container(
            alignment=ft.alignment.center,
            on_click=lambda _: self.date_picker.pick_date(),
            content=ft.Row(
                controls=[
                    self.text_field_date,
                    ft.Icon(
                        name=ft.icons.CALENDAR_MONTH,
                        color=ft.colors.BLUE_200,
                        size=40,
                    )
                ]
            )
        )
        self.container_time_picker = ft.Container(
            on_click=lambda _: self.time_picker.pick_time(),
            content=ft.Row(
                controls=[
                    self.text_field_time,
                    ft.Icon(
                        name=ft.icons.ACCESS_TIME_FILLED_OUTLINED,
                        color=ft.colors.BLUE_200,
                        size=40,
                    )
                ]
            )
        )

        # Слайдер приоритета и выпадающий список категорий
        self.slider_priority = ft.Slider(
            min=0,
            max=100,
            divisions=10,
            value=0,
            label="{value}%",
        )
        self.dropdown_category = ft.Dropdown(
            label="Категория",
            hint_text="Неопределенные",
            options=[
                ft.dropdown.Option(category["category_name"])
                for category in fetch_categories()
            ],
            value=None
        )

        # Формирование страницы создания задачи
        self.row_task_form = self.create_task_form()

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

    def create_task_form(self):
        # Сборка представления
        return ft.Row(
            controls=[
                ft.Container(
                    width=700,
                    height=610,
                    padding=ft.padding.only(
                        left=5,
                        right=5,
                    ),
                    content=ft.Column(
                        scroll="ALWAYS",
                        controls=[
                            self.container_section_name,
                            self.text_field_name_task,
                            ft.Container(height=15),

                            self.text_field_description_task,
                            ft.Container(height=15),

                            ft.Row(
                                alignment="CENTER",
                                controls=[self.container_date_picker]
                            ),
                            ft.Container(height=15),

                            ft.Row(
                                alignment="CENTER",
                                controls=[self.container_time_picker]
                            ),
                            ft.Container(height=15),

                            ft.Column(
                                controls=[
                                    ft.Text(value="Укажите приоритет:"),
                                    self.slider_priority
                                ]
                            ),
                            ft.Container(height=15),

                            self.dropdown_category,
                            ft.Container(height=15),

                            ft.Row(
                                alignment="CENTER",
                                controls=[
                                    ft.ElevatedButton(
                                        text="Готово",
                                        on_click=self.button_clicked
                                    ),
                                ]
                            ),

                        ]
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

    def on_date_changed(self, e):
        # Обработка изменения даты
        self.text_field_date.value = e.control.value.strftime('%m/%d/%Y')
        self.page.update()

    def on_time_changed(self, e):
        # Обработка изменения времени
        self.text_field_time.value = e.control.value.strftime('%H:%M')
        self.page.update()

    def button_clicked(self, e):
        # Обработка нажатия кнопки "Готово"

        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        task_name = self.text_field_name_task.value
        task_description = self.text_field_description_task.value
        task_due_date = datetime.datetime.combine(
            self.date_picker.value.date(), self.time_picker.value
        )
        task_priority = self.slider_priority.value
        task_category = self.dropdown_category.value

        char_count = len(task_name)
        current_datetime = datetime.datetime.combine(
            self.current_date, self.current_time
        )

        if char_count == 0:
            dlg = show_alert_dialog(
                page=self.page,
                title="Поле названия задачи не должно быть пустым.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif char_count > 50:
            dlg = show_alert_dialog(
                page=self.page,
                title="Название задачи не должно превышать 50 символов.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif task_due_date < current_datetime:
            dlg = show_alert_dialog(
                page=self.page,
                title="Выбранное время уже прошло.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )

        else:
            result, error_or_task_id = add_task(
                name=task_name,
                description=task_description,
                due_date=task_due_date,
                priority=int(task_priority),
                category_name=task_category,
            )

            if result:
                task_scheduler = TaskScheduler()
                task_scheduler.schedule_task(
                    error_or_task_id,
                    task_due_date,
                    send_notification,
                    "Напоминание",
                    task_name,
                )

                dlg = show_alert_dialog(
                    page=self.page,
                    title="Задача успешно создана!",
                    buttons=["Закрыть"],
                    funcs=[close_alert_dialog],
                    alignment=ft.MainAxisAlignment.CENTER
                )

            else:
                dlg = show_alert_dialog(
                    page=self.page,
                    title=error_or_task_id,
                    buttons=["Закрыть"],
                    funcs=[close_alert_dialog],
                    alignment=ft.MainAxisAlignment.CENTER
                )


class EditTaskView(ft.Container):
    def __init__(self, page, task_id):
        super().__init__()
        self.current_date = datetime.datetime.now().date()
        self.current_time = datetime.datetime.now().time()

        self.page = page
        self.task_id = int(task_id)
        self.setup_ui()

    def setup_ui(self):
        self.init_elements()

        # Собираем весь интерфейс
        self.content = ft.Stack(
            controls=[
                self.container_back_button,
                self.row_task_form,
            ]
        )

    def init_elements(self):
        self.task_data = fetch_tasks(
            task_id=self.task_id
        )[0]

        # Название раздела
        self.container_section_name = ft.Container(
            alignment=ft.alignment.center,
            content=ft.Text(
                value="Редактирование задачи",
                size=30
            ),
        )

        # Input-поля
        self.text_field_name_task = ft.TextField(
            label="Введите название",
            hint_text="Например, Подготовка к экзаменам..",
            counter_text="Введено 0 из 50 возможных символов",
            # Добавляем обработчик события изменения текста
            on_change=self.on_text_changed,
            value=self.task_data["name"],
        )
        self.text_field_description_task = ft.TextField(
            label="Введите описание",
            multiline=True,
            min_lines=1,
            max_lines=10,
            value=self.task_data["description"],
        )

        due_date = datetime.datetime.strptime(
            self.task_data["due_date"], '%Y-%m-%d %H:%M:%S'
        )

        # Input-поля, отображающие дату и время
        self.text_field_date = ft.TextField(
            label="Дата",
            disabled=True,
            value=due_date.strftime('%m/%d/%Y')
        )
        self.text_field_time = ft.TextField(
            label="Время",
            disabled=True,
            value=due_date.strftime('%H:%M'),
        )

        # Объекты выбора даты и времени
        self.date_picker = ft.DatePicker(
            on_change=self.on_date_changed,
            cancel_text="Отмена",
            confirm_text="Ок",
            error_format_text="Недопустимый формат даты",
            error_invalid_text="Дата вне допустимого диапазона",
            field_label_text="Введите дату",
            help_text="Выберите дату",
            switch_to_calendar_icon="Ввести вручную",
            switch_to_input_icon="Вернуться к календарю",
            first_date=due_date.date(),
            value=due_date.date(),
        )
        self.time_picker = ft.TimePicker(
            on_change=self.on_time_changed,
            cancel_text="Отмена",
            confirm_text="Ок",
            error_invalid_text="Недопустимый формат времени",
            hour_label_text="Часы",
            minute_label_text="Минуты",
            help_text="Введите время",
            value=due_date.time()
        )
        self.page.overlay.extend(
            [self.date_picker, self.time_picker]
        )

        self.container_date_picker = ft.Container(
            alignment=ft.alignment.center,
            on_click=lambda _: self.date_picker.pick_date(),
            content=ft.Row(
                controls=[
                    self.text_field_date,
                    ft.Icon(
                        name=ft.icons.CALENDAR_MONTH,
                        color=ft.colors.BLUE_200,
                        size=40,
                    )
                ]
            )
        )
        self.container_time_picker = ft.Container(
            on_click=lambda _: self.time_picker.pick_time(),
            content=ft.Row(
                controls=[
                    self.text_field_time,
                    ft.Icon(
                        name=ft.icons.ACCESS_TIME_FILLED_OUTLINED,
                        color=ft.colors.BLUE_200,
                        size=40,
                    )
                ]
            )
        )

        # Слайдер приоритета и выпадающий список категорий
        self.slider_priority = ft.Slider(
            min=0,
            max=100,
            divisions=10,
            value=self.task_data["priority"],
            label="{value}%",
        )
        self.dropdown_category = ft.Dropdown(
            label="Категория",
            hint_text=self.task_data["category"],
            options=[
                ft.dropdown.Option(category["category_name"])
                for category in fetch_categories()
            ],
            value=self.task_data["category"]
        )
        self.dropdown_status = ft.Dropdown(
            label="Статус",
            hint_text=self.task_data["status"],
            options=[
                ft.dropdown.Option(status)
                for status in fetch_statuses()
            ],
            value=self.task_data["status"]
        )

        # Формирование страницы создания задачи
        self.row_task_form = self.create_task_form()

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

    def on_text_changed(self, e):
        # Обновление счетчика символов
        e.control.counter_text = (
            f"Введено {len(e.control.value)} из 50 возможных символов"
        )
        self.page.update()

    def on_date_changed(self, e):
        # Обработка изменения даты
        self.text_field_date.value = e.control.value.strftime('%m/%d/%Y')
        self.page.update()

    def on_time_changed(self, e):
        # Обработка изменения времени
        self.text_field_time.value = e.control.value.strftime('%H:%M')
        self.page.update()

    def create_task_form(self):
        # Сборка представления
        return ft.Row(
            controls=[
                ft.Container(
                    width=700,
                    height=610,
                    padding=ft.padding.only(
                        left=5,
                        right=5,
                    ),
                    content=ft.Column(
                        scroll="ALWAYS",
                        controls=[
                            self.container_section_name,
                            self.text_field_name_task,
                            ft.Container(height=15),

                            self.text_field_description_task,
                            ft.Container(height=15),

                            ft.Row(
                                alignment="CENTER",
                                controls=[self.container_date_picker]
                            ),
                            ft.Container(height=15),

                            ft.Row(
                                alignment="CENTER",
                                controls=[self.container_time_picker]
                            ),
                            ft.Container(height=15),

                            ft.Column(
                                controls=[
                                    ft.Text(value="Укажите приоритет:"),
                                    self.slider_priority
                                ]
                            ),
                            ft.Container(height=15),

                            self.dropdown_category,
                            ft.Container(height=15),

                            self.dropdown_status,
                            ft.Container(height=15),

                            ft.Row(
                                alignment="CENTER",
                                controls=[
                                    ft.ElevatedButton(
                                        text="Готово",
                                        on_click=self.button_clicked
                                    ),
                                ]
                            ),

                        ]
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def button_clicked(self, e):

        def close_alert_dialog(e):
            close_dialog_and_update(dlg=dlg, page=self.page)

        task_name = self.text_field_name_task.value
        task_description = self.text_field_description_task.value
        task_due_date = datetime.datetime.combine(
            self.date_picker.value.date(), self.time_picker.value
        )
        task_priority = self.slider_priority.value
        task_category = self.dropdown_category.value
        task_status = self.dropdown_status.value

        char_count = len(task_name)
        current_datetime = datetime.datetime.combine(
            self.current_date, self.current_time
        )

        if char_count == 0:
            dlg = show_alert_dialog(
                page=self.page,
                title="Поле названия задачи не должно быть пустым.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif char_count > 50:
            dlg = show_alert_dialog(
                page=self.page,
                title="Название задачи не должно превышать 50 символов.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif task_due_date < current_datetime:
            dlg = show_alert_dialog(
                page=self.page,
                title="Выбранное время уже прошло.",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )

        else:
            result, error = update_task(
                task_id=self.task_id,
                name=task_name,
                description=task_description,
                due_date=task_due_date,
                priority=int(task_priority),
                status_name=task_status,
                category_name=task_category,
            )

            if result:
                task_scheduler = TaskScheduler()
                task_scheduler.clear_scheduled_task(
                    self.task_id
                )
                task_scheduler.schedule_task(
                    self.task_id,
                    task_due_date,
                    send_notification,
                    "Напоминание",
                    task_name,
                )

                dlg = show_alert_dialog(
                    page=self.page,
                    title="Задача успешно изменена!",
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
