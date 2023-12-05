import flet as ft

from database import add_category
from utils import show_alert_dialog


def create_categories_view(page: ft.Page) -> ft.Container:
    def close_alert_dialog(e):
        dlg.open = False
        page.update()

    # Обработка данных
    def button_clicked(e):
        global dlg
        category_name = text_field_name_category.value
        char_count = len(category_name)

        if char_count == 0:
            dlg = show_alert_dialog(
                page=page,
                title="Поле названия категории не должно быть пустым!",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        elif char_count > 50:
            dlg = show_alert_dialog(
                page=page,
                title="Название категории не должно превышать 50 символов!",
                buttons=["Закрыть"],
                funcs=[close_alert_dialog],
                alignment=ft.MainAxisAlignment.CENTER
            )
        else:
            result, error = add_category(category_name)

            if result:
                dlg = show_alert_dialog(
                    page=page,
                    title="Категория успешно создана!",
                    buttons=["Главное меню", "Закрыть"],
                    funcs=[lambda _: page.go("/"), close_alert_dialog],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            else:
                dlg = show_alert_dialog(
                    page=page,
                    title=error,
                    buttons=["Главное меню", "Закрыть"],
                    funcs=[lambda _: page.go("/"), close_alert_dialog],
                    alignment=ft.MainAxisAlignment.CENTER
                )

    def on_text_changed(e):
        char_count = len(e.control.value)

        # Обновляем text_field_name_category
        text_field_name_category.counter_text = f"Введено {char_count} из 50 возможных символов"
        page.update()

    text_field_name_category = ft.TextField(
        label="Введите название категории",
        hint_text="Например, Домашние дела, Работа, Учеба...",
        counter_text="Введено 0 из 50 возможных символов",
        on_change=on_text_changed,  # Добавляем обработчик события изменения текста
    )

    # Кнопка назад
    back_button = ft.Container(
        padding=ft.padding.only(
            top=10,
            left=5,
            right=5,
            bottom=10
        ),
        on_click=lambda _: page.go("/"),
        content=ft.Icon(
            name=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED,
        ),
    )

    # Сборка input-полей
    categories_create_page = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=600,
                padding=ft.padding.only(
                    top=250,
                    left=5,
                    right=5,
                    bottom=10
                ),
                content=ft.Column(
                    controls=[
                        text_field_name_category,
                        ft.ElevatedButton(
                            text="Готово",
                            on_click=button_clicked
                        )
                    ],
                )
            )
        ]
    )

    create_categories_container = ft.Container(
        content=ft.Stack(
            controls=[
                back_button,
                categories_create_page
            ],
        )

    )

    return create_categories_container