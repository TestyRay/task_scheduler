categories_table = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
"""

statuses_table = """
CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
"""

tasks_table = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    creation_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    category_id INTEGER,
    FOREIGN KEY (status_id) REFERENCES statuses(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
"""
