import sqlite3

from typing import List, Dict


# Функция для создания базы данных и таблиц
def setup_database():
    conn = sqlite3.connect('organizer.db')
    cursor = conn.cursor()

    # Создание таблицы categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    """)

    # Создание таблицы tasks с полем category_id
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        creation_date TEXT NOT NULL,
        due_date TEXT,
        priority INTEGER NOT NULL,
        status TEXT NOT NULL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)

    # Добавление начальных категорий
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