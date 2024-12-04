import sqlite3
from tkinter import Tk, Toplevel, Label, Listbox, messagebox, END
from interface import configure_theme, create_rounded_entry, create_rounded_button, create_rounded_label
from customtkinter import CTk


def initialize_database():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Создание таблицы для хранения информации о читателе
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readers (
            reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone_number TEXT NOT NULL UNIQUE,
            active_debts BOOLEAN NOT NULL DEFAULT 0,
            password TEXT NOT NULL, 
            role TEXT NOT NULL 
        )
    """)

    # Создание таблицы для хранения информации о книге
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)

    # Создание таблицы для хранения информации о экземпляре книги
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_instances (
            book_instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            storage_shelf TEXT NOT NULL,
            publisher TEXT NOT NULL,
            year INTEGER NOT NULL,
            availability BOOLEAN NOT NULL DEFAULT 1,
            last_issue_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        )
    """)

    # Создание таблицы для хранения информации о журнальной публикации
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            issue TEXT NOT NULL,
            publisher TEXT NOT NULL,
            publication_date TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)

    # Создание таблицы для хранения информации об экземпляре журнала
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_instances (
            journal_instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_id INTEGER NOT NULL,
            availability BOOLEAN NOT NULL DEFAULT 1,
            last_issue_date TEXT,
            FOREIGN KEY (journal_id) REFERENCES journals(journal_id) ON DELETE CASCADE
        )
    """)

    # Создание таблицы для хранения информации о выдаче литературы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_period INTEGER NOT NULL,
            FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON DELETE CASCADE
        )
    """)

    # Создание таблицы для хранения информации об очереди на литературу
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queues (
            queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            queue_position INTEGER NOT NULL,
            request_status TEXT NOT NULL,
            FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON DELETE CASCADE
        )
    """)

    # Создание таблицы для хранения информации о штрафах
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fines (
            fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            fine_date TEXT NOT NULL,
            related_loan_id INTEGER NOT NULL,
            FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON DELETE CASCADE,
            FOREIGN KEY (related_loan_id) REFERENCES loans(loan_id) ON DELETE CASCADE
        )
    """)

    # Добавление тестовых данных в таблицу readers
    cursor.execute("""
        INSERT OR IGNORE INTO readers (first_name, last_name, phone_number, password, role) VALUES
        ('Genadiy', 'Pivovarov', '89965476893', '123', 'Гость'),
        ('Lenny', 'First', '88005353535', '123', 'Библиотекарь')
    """)
    conn.commit()
    conn.close()

def login_user(reader_id, password):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT reader_id, password, role FROM readers WHERE reader_id = ? AND password = ?", (reader_id, password))
    reader = cursor.fetchone()
    conn.close()
    return reader

def open_login_window():
    def on_login():
        reader_id = reader_id_entry.get()
        password = password_entry.get()
        reader = login_user(reader_id, password)
        if reader:
            reader_id, password, role = reader
            login_window.destroy()  # Закрыть окно авторизации
            if role == 'Библиотекарь':
                open_admin_dashboard(reader_id)
                ####################
                ####################
            else:
                open_user_dashboard(reader_id)
                ####################
                ####################
        else:
            messagebox.showerror("Ошибка", "Неверный уникальный ID или пароль")

    login_window = Toplevel(root)
    configure_theme(login_window)
    login_window.title("Авторизация")
    login_window.geometry("400x300")
    create_rounded_label(login_window, text="Уникальный ID пользователя:").pack(pady=10)
    reader_id_entry = create_rounded_entry(login_window)
    reader_id_entry.pack(pady=10)

    create_rounded_label(login_window, text="Пароль:").pack(pady=10)
    password_entry = create_rounded_entry(login_window, show="*")
    password_entry.pack(pady=10)
    create_rounded_button(login_window, text="Войти", command=on_login).pack(pady=10)




def open_user_dashboard(reader_id):
    # Здесь будет код для отображения главной страницы пользователя (например, просмотр книг)
    pass

def open_admin_dashboard(reader_id):
    # Здесь будет код для отображения главной страницы администратора (например, управление книгами)
    pass

def main_window():
    create_rounded_label(root, text="Library App").pack(pady=10)
    create_rounded_button(root, text="Вход для пользователей", command=open_login_window).pack(pady=5)

if __name__ == "__main__":
    root = CTk()
    root.title("Библиотека")
    configure_theme(root)
    initialize_database()
    main_window()
    root.mainloop()