import pymorphy3

import flet as ft

from plyer import notification


# FLET

def navigate_to_route(page, route, dlg=None):
    page.go(route)
    if dlg:
        close_dialog_and_update(
            dlg=dlg,
            page=page,
        )


def close_dialog_and_update(dlg, page):
    dlg.open = False
    page.update()

def show_alert_dialog(page, title, buttons, funcs, alignment):
    dlg = create_alert_dialog(
        title=title,
        text_button=buttons,
        func_button=funcs,
        alignment_button=alignment
    )
    page.dialog = dlg
    dlg.open = True
    page.update()
    return dlg

def create_alert_dialog(title, text_button, func_button, alignment_button):

    alert_dialog = ft.AlertDialog(
        title=ft.Text(title),
        actions=[
            ft.TextButton(
                text=text,
                on_click=func
            ) for text, func in zip(text_button, func_button)
        ],
        actions_alignment=alignment_button,
    )
    return alert_dialog


# PYMORPHY
def pluralize_word(word: str, number: int) -> str:
    """
    Склоняет заданное слово в соответствии с числом.

    :param str word: Слово для склонения.
    :param int number: Число, в соответствии с которым нужно склонять слово.
    :return: Слово в нужном склонении.
    """
    morph = pymorphy3.MorphAnalyzer()
    parsed_word = morph.parse(word)[0]

    return parsed_word.make_agree_with_number(number).word


# PLYER
def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='Планировщик задач'
    )


