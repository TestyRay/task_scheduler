import flet as ft

from views import MainWindow
from database import setup_database


def main():
    # Создание базы данных и таблиц
    setup_database()

    # Запуск приложения flet
    ft.app(target=MainWindow)


if __name__ == '__main__':
    main()