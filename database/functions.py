import sqlite3
from typing import List, Dict

from .models import categories_table, tasks_table

def setup_database():
    """
    Инициализирует базу данных приложения. Создает таблицы 'categories' и 'tasks', а также
    добавляет начальные категории ('Личные', 'Работа', 'Учеба').
    """
    conn = sqlite3.connect('organizer.db')
    cursor = conn.cursor()

    cursor.execute(categories_table)
    cursor.execute(tasks_table)

    initial_categories = ["Личные", "Работа", "Учеба"]
    for category in initial_categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))

    conn.commit()
    conn.close()

# Функция для добавления категории
def add_category(name):
    conn = sqlite3.connect('organizer.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


# Функция для добавления задачи с категорией
def add_task(name, description, creation_date, due_date, priority, status, category_name):
    conn = sqlite3.connect('organizer.db')
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

    conn = sqlite3.connect('organizer.db')
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
