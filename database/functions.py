import sqlite3
from typing import List, Dict

from .models import categories_table, tasks_table

DATABASE = "organizer.db"


def setup_database():
    """
    Инициализирует базу данных приложения. Создает таблицы 'categories' и 'tasks', а также
    добавляет начальные категории ('Личные', 'Работа', 'Учеба').
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(categories_table)
    cursor.execute(tasks_table)

    initial_categories = ["Личные", "Работа", "Учеба"]
    for category in initial_categories:
        add_category(
            category_name=category,
            insert_or_ignore=True,
        )

    conn.commit()
    conn.close()


def add_category(category_name: str, insert_or_ignore: bool = False) -> tuple:
    """
    Добавляет новую категорию в базу данных.

    :param category_name: Название категории, которую нужно добавить.
    :param insert_or_ignore: Если True, то команда INSERT будет выполнена с ключевым словом OR IGNORE,
                             что позволяет избежать ошибок при попытке добавить дублирующуюся категорию.
                             По умолчанию False.
    :return: Кортеж (bool, str), где первый элемент - флаг успешности операции, второй - описание ошибки, если она произошла.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if insert_or_ignore:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category_name,))
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))

        conn.commit()
        return True, None  # Возвращает True, если нет ошибок

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            return False, "Название категории должно быть уникальным."
        else:
            return False, str(e)  # Возвращает описание ошибки, если она не связана с уникальностью

    except Exception as e:
        return False, str(e)  # Возвращает описание любой другой ошибки

    finally:
        if conn:
            conn.close()


# Функция для добавления задачи с категорией
def add_task(name, description, creation_date, due_date, priority, status, category_name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Находим ID категории по имени
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_id = cursor.fetchone()

    if category_id:
        cursor.execute(
            "INSERT INTO tasks (name, description, creation_date, due_date, priority, status, category_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, description, creation_date, due_date, priority, status, category_id[0]))
    else:
        print(f"Категория {category_name} не найдена!")

    conn.commit()
    conn.close()


def fetch_categories() -> List[Dict[str, int]]:
    """
    Извлечь список категорий и количество задач, привязанных к каждой категории, из базы данных.

    :return: Список словарей, где каждый словарь содержит название категории и количество задач,
             привязанных к этой категории.
    :rtype: List[Dict[str, int]]
    """

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.name AS category_name, 
            COUNT(t.id) AS task_count
        FROM 
            categories c
        LEFT JOIN 
            tasks t ON c.id = t.category_id
        GROUP BY 
            c.name
    """)

    result = cursor.fetchall()
    categories = [{"name": row[0], "task_count": row[1]} for row in result]

    conn.close()

    return categories
