from datetime import datetime
import sqlite3
from typing import (
    Optional,
    Tuple,
    List,
    Dict,
    Any,
)
from .models import (
    categories_table,
    statuses_table,
    tasks_table,
)

DATABASE = "organizer.db"


def setup_database():
    """
    Инициализирует базу данных приложения.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(categories_table)
    cursor.execute(statuses_table)
    cursor.execute(tasks_table)

    # Добавление начальных категории
    initial_categories = ["Неопределенные"]

    for category in initial_categories:
        add_category(
            category_name=category,
            insert_or_ignore=True,
        )

    # Добавление начальных статусов
    initial_statuses = ["Новая", "В процессе", "Завершена"]
    for status in initial_statuses:
        add_status(
            status_name=status,
            insert_or_ignore=True,
        )

    conn.commit()
    conn.close()


def add_category(
        category_name: str,
        insert_or_ignore: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Добавляет новую категорию в базу данных.

    :param category_name: Название категории, которую нужно добавить в БД.
    :param insert_or_ignore: Если True, категория не добавляется в БД, если
                             уже существует. По умолчанию False.

    :return: Кортеж, где первый элемент - флаг успешности операции, второй -
             описание ошибки, если она произошла.
    :rtype: Tuple[bool, Optional[str]]
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if insert_or_ignore:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                (category_name,)
            )
        else:
            cursor.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category_name,)
            )

        conn.commit()
        return True, None

    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed" in str(error):
            return False, "Категория с таким именем уже создана."
        else:
            # Возвращает описание ошибки, если она не связана с уникальностью
            return False, str(error)

    except Exception as error:
        # Возвращает описание любой другой ошибки
        return False, str(error)

    finally:
        if conn:
            conn.close()


def add_status(
        status_name: str,
        insert_or_ignore: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Добавляет новый статус в базу данных.

    :param status_name: Название статуса, который нужно добавить в БД.
    :param insert_or_ignore: Если True, статус не добавляется в БД, если
                             уже существует. По умолчанию False.

    :return: Кортеж, где первый элемент - флаг успешности операции, второй -
             описание ошибки, если она произошла.
    :rtype: Tuple[bool, Optional[str]]
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if insert_or_ignore:
            cursor.execute(
                "INSERT OR IGNORE INTO statuses (name) VALUES (?)",
                (status_name,)
            )
        else:
            cursor.execute(
                "INSERT INTO statuses (name) VALUES (?)",
                (status_name,)
            )

        conn.commit()
        return True, None  # Успешное добавление статуса

    except sqlite3.IntegrityError as error:
        return False, f"Ошибка базы данных: {error}"

    except Exception as error:
        return False, f"Неизвестная ошибка: {error}"

    finally:
        if conn:
            conn.close()


def add_task(
        name: str,
        description: str,
        due_date: datetime,
        priority: int,
        status: Optional[str] = None,
        category_name: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Добавляет новую задачу в базу данных с возможностью привязки к категории.

    :param name: Название задачи.
    :param description: Описание задачи.
    :param due_date: Срок задачи в виде объекта datetime.
    :param priority: Приоритет задачи.
    :param status: Статус задачи. Если None, назначается первый доступный статус.
    :param category_name: Название категории, к которой принадлежит задача.

    :return: Кортеж, где первый элемент - флаг успешности операции, второй -
             описание ошибки, если она произошла.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_due_date = due_date.strftime("%Y-%m-%d %H:%M:%S")

        if not status:
            cursor.execute("SELECT id FROM statuses ORDER BY id LIMIT 1")
            status_row = cursor.fetchone()
            status_id = status_row[0] if status_row else None
        else:
            cursor.execute("SELECT id FROM statuses WHERE name = ?", (status,))
            status_row = cursor.fetchone()
            status_id = status_row[0] if status_row else None

        category_id = 1
        if category_name:
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            category_row = cursor.fetchone()
            if category_row:
                category_id = category_row[0]
            else:
                return False, f"Категория с именем '{category_name}' не найдена."

        task_values = (
            name, description, creation_date, formatted_due_date,
            priority, status_id, category_id,
        )
        cursor.execute(
            """
            INSERT INTO tasks 
            (name, description, creation_date, due_date, priority, status_id, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            task_values
        )

        new_task_id = cursor.lastrowid  # Получение ID новой задачи
        conn.commit()

        return True, new_task_id

    except sqlite3.IntegrityError as error:
        return False, f"Ошибка базы данных: {error}"

    except Exception as error:
        return False, f"Неизвестная ошибка: {error}"

    finally:
        if conn:
            conn.close()


def fetch_categories(
        category_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Извлекает информацию о категориях и всех привязанных к ним задачах.

    :param category_id: ID категории для выборки конкретной категории. По умолчанию None,
                        что означает выборку всех категорий.

    :return: Список словарей, каждый из которых содержит информацию о
             категории и связанных с ней задачах.
    :rtype: List[Dict[str, Any]]
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if category_id:
        # Если передан category_id, выполнить выборку только для этой категории
        cursor.execute("""
            SELECT c.id as category_id, c.name as category_name, 
                   t.id as task_id, t.name as task_name, t.description, 
                   t.creation_date, t.due_date, t.priority, s.name as status_name
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id
            LEFT JOIN statuses s ON t.status_id = s.id
            WHERE c.id = ?
            """, (category_id,))
    else:
        # Если category_id не передан, выполнить выборку для всех категорий
        cursor.execute("""
            SELECT c.id as category_id, c.name as category_name, 
                   t.id as task_id, t.name as task_name, t.description, 
                   t.creation_date, t.due_date, t.priority, s.name as status_name
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id
            LEFT JOIN statuses s ON t.status_id = s.id
            """)

    categories = {}
    for row in cursor.fetchall():
        category_id = row[0]
        if category_id not in categories:
            categories[category_id] = {
                "category_id": category_id,
                "category_name": row[1],
                "tasks": []
            }

        if row[2]:  # Если есть задача, связанная с категорией
            task = {
                "task_id": row[2],
                "task_name": row[3],
                "description": row[4],
                "creation_date": row[5],
                "due_date": row[6],
                "priority": row[7],
                "status_name": row[8]
            }
            categories[category_id]["tasks"].append(task)

    conn.close()
    return list(categories.values())


def fetch_tasks(
        due_date: datetime = None,
        include_completed: bool = True,
        task_id: int = None
) -> List[Dict[str, Any]]:
    """
    Извлекает задачи из базы данных, у которых срок выполнения
    соответствует указанной дате. Если дата не указана, используется
    текущая дата. Задачи сортируются по убыванию приоритета.

    :param due_date: Объект datetime, представляющий дату, по
                     которой необходимо найти задачи.
    :param include_completed: Флаг для включения/исключения завершенных задач.
    :param task_id: ID конкретной задачи, по которой нужно извлечь информацию.
                    По умолчанию None, что означает извлечение всех задач.
    :return: Список словарей, каждый из которых содержит информацию
             о задаче, включая имя, описание, дату создания, срок
             выполнения, приоритет, статус и категорию.
    :rtype: List[Dict[str, Any]]
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if task_id is not None:
        cursor.execute("""
                SELECT t.id, t.name, t.description, t.creation_date, t.due_date, t.priority, 
                       s.name as status, c.name as category
                FROM tasks t
                LEFT JOIN statuses s ON t.status_id = s.id
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?
                """, (task_id,))
    else:
        if due_date is None:
            due_date = datetime.now()
        formatted_due_date = due_date.strftime("%Y-%m-%d")

        # SQL запрос для выбора задач по дате с сортировкой по убыванию приоритета
        if include_completed:
            cursor.execute("""
                    SELECT t.id, t.name, t.description, t.creation_date, t.due_date, t.priority, 
                           s.name as status, c.name as category
                    FROM tasks t
                    LEFT JOIN statuses s ON t.status_id = s.id
                    LEFT JOIN categories c ON t.category_id = c.id
                    WHERE t.due_date LIKE ?
                    ORDER BY t.priority DESC
                    """, (formatted_due_date + "%",))
        else:
            cursor.execute("""
                    SELECT t.id, t.name, t.description, t.creation_date, t.due_date, t.priority, 
                           s.name as status, c.name as category
                    FROM tasks t
                    LEFT JOIN statuses s ON t.status_id = s.id
                    LEFT JOIN categories c ON t.category_id = c.id
                    WHERE t.due_date LIKE ? AND s.name != 'Завершена'
                    ORDER BY t.priority DESC
                    """, (formatted_due_date + "%",))

    tasks = cursor.fetchall()
    conn.close()

    # Формирование списка задач
    return [
        {
            "id": task[0],
            "name": task[1],
            "description": task[2],
            "creation_date": task[3],
            "due_date": task[4],
            "priority": task[5],
            "status": task[6],
            "category": task[7]
        }
        for task in tasks
    ]

def delete_category(
        category_id: int,
        delete_tasks: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Удаляет категорию из базы данных по её идентификатору.

    :param category_id: Идентификатор категории.
    :param delete_tasks: Если True, удаляются и категория и привязанные к ней задачи.
                         Если False, категория удаляется, а задачи перепривязываются
                                     к категории с id = 1.

    :return: Кортеж, где первый элемент - флаг успешности операции, второй -
             описание ошибки, если она произошла.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if delete_tasks:
            # Удаление всех задач, связанных с этой категорией
            cursor.execute("DELETE FROM tasks WHERE category_id = ?", (category_id,))
        else:
            # Перепривязка задач к категории с id = 1
            cursor.execute("UPDATE tasks SET category_id = 1 WHERE category_id = ?", (category_id,))

        # Удаление самой категории
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))

        conn.commit()
        return True, None

    except sqlite3.IntegrityError as error:
        return False, f"Ошибка базы данных: {error}"

    except Exception as error:
        return False, f"Неизвестная ошибка: {error}"

    finally:
        if conn:
            conn.close()

def update_category(
        category_id: int,
        new_name: str
) -> Tuple[bool, Optional[str]]:
    """
    Обновляет название категории в базе данных.

    :param category_id: Идентификатор категории для обновления.
    :param new_name: Новое название категории.

    :return: Кортеж, где первый элемент - флаг успешности операции, второй -
             описание ошибки, если она произошла.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Обновление названия категории
        cursor.execute(
            "UPDATE categories SET name = ? WHERE id = ?",
            (new_name, category_id)
        )

        conn.commit()
        return True, None

    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed" in str(error):
            return False, "Категория с таким названием уже существует."
        return False, f"Ошибка базы данных: {error}"

    except Exception as error:
        return False, f"Неизвестная ошибка: {error}"

    finally:
        if conn:
            conn.close()

def change_task_status(
        task_id: int,
        status_id: int
) -> Tuple[bool, Optional[str]]:
    """
    Меняет статус задачи на указанный.

    :param task_id: ID задачи, статус которой нужно изменить.
    :param status_id: ID нового статуса для задачи.

    :return: Кортеж, где первый элемент - флаг успешности операции, второй -
             описание ошибки, если она произошла.
    :rtype: Tuple[bool, Optional[str]]
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("UPDATE tasks SET status_id = ? WHERE id = ?", (status_id, task_id))
        conn.commit()

        return True, None

    except sqlite3.IntegrityError as error:
        return False, f"Ошибка базы данных: {error}"

    except Exception as error:
        return False, f"Неизвестная ошибка: {error}"

    finally:
        if conn:
            conn.close()

def delete_task(task_id: int) -> Tuple[bool, Optional[str]]:
    """
    Удаляет задачу из базы данных по её ID.

    :param task_id: ID задачи, которую нужно удалить.

    :return: Кортеж, где первый элемент - флаг успешности операции, второй -
             описание ошибки, если она произошла.
    :rtype: Tuple[bool, Optional[str]]
    """
    conn = None

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

        return True, None

    except sqlite3.IntegrityError as error:
        return False, f"Ошибка базы данных: {error}"

    except Exception as error:
        return False, f"Неизвестная ошибка: {error}"

    finally:
        if conn:
            conn.close()

def update_task(
    task_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    priority: Optional[int] = None,
    status_name: Optional[str] = None,
    category_name: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Изменяет значения задачи в базе данных по её ID.

    :param task_id: ID задачи, которую нужно изменить.
    :param name: Новое название задачи. Если None, название остается без изменений.
    :param description: Новое описание задачи. Если None, описание остается без изменений.
    :param due_date: Новый срок выполнения задачи. Если None, срок остается без изменений.
    :param priority: Новый приоритет задачи. Если None, приоритет остается без изменений.
    :param status_name: Новый статус задачи. Если None, статус остается без изменений.
    :param category_name: Новая категория задачи. Если None, категория остается без изменений.

    :return: Флаг успешного выполнения операции.
    :rtype: Tuple[bool, Optional[str]]
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Формирование SQL-запроса для обновления значений задачи
        update_values = []
        if name:
            update_values.append(("name", name))
        if description:
            update_values.append(("description", description))
        if due_date:
            formatted_due_date = due_date.strftime("%Y-%m-%d %H:%M:%S")
            update_values.append(("due_date", formatted_due_date))
        if priority is not None:
            update_values.append(("priority", priority))
        if status_name is not None:
            cursor.execute("SELECT id FROM statuses WHERE name = ?", (status_name,))
            status_row = cursor.fetchone()
            if status_row:
                update_values.append(("status_id", status_row[0]))
        if category_name is not None:
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            category_row = cursor.fetchone()
            if category_row:
                update_values.append(("category_id", category_row[0]))

        if update_values:
            set_values = ', '.join([f"{field} = ?" for field, _ in update_values])
            set_values_args = [value for _, value in update_values]
            set_values_args.append(task_id)

            cursor.execute(f"UPDATE tasks SET {set_values} WHERE id = ?", set_values_args)
            conn.commit()

        return True, None

    except sqlite3.IntegrityError as error:
        return False, f"Ошибка базы данных: {error}"

    except Exception as error:
        return False, f"Неизвестная ошибка: {error}"

    finally:
        if conn:
            conn.close()

def fetch_statuses() -> list:
    """
    Извлекает все названия статусов из базы данных.

    :return: Список названий статусов.
    :rtype: list
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM statuses")
    status_rows = cursor.fetchall()

    statuses = [row[0] for row in status_rows]
    conn.close()

    return statuses
