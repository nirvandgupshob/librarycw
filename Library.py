import sqlite3
from tkinter import Tk, Toplevel, Label, Listbox, messagebox, END, StringVar, OptionMenu, Entry, Button, Radiobutton
from interface import configure_theme, create_rounded_entry, create_rounded_button, create_rounded_label
from customtkinter import CTk
from datetime import datetime


def initialize_database():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Таблица читателей
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

    # Таблица книг
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)

    # Таблица экземпляров книг
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_instances (
            book_instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            storage_shelf TEXT NOT NULL,
            publisher TEXT NOT NULL,
            year INTEGER NOT NULL,
            availability BOOLEAN NOT NULL DEFAULT 1,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        )
    """)

    # Таблица журнальных публикаций
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            issue TEXT NOT NULL,
            publication_date TEXT NOT NULL,
            section TEXT NOT NULL,
            availability BOOLEAN NOT NULL DEFAULT 1,
            storage_shelf TEXT NOT NULL
        )
    """)

    # Таблица выдачи литературы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            book_instance_id INTEGER DEFAULT NULL,
            journal_id INTEGER DEFAULT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            actual_date TEXT DEFAULT NULL,
            FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON DELETE CASCADE,
            FOREIGN KEY (book_instance_id) REFERENCES book_instances(book_instance_id) ON DELETE CASCADE,
            FOREIGN KEY (journal_id) REFERENCES journals(journal_id) ON DELETE CASCADE
        )
    """)

    # Таблица очереди
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queues (
            queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            book_instance_id INTEGER DEFAULT NULL,
            journal_id INTEGER DEFAULT NULL,
            queue_position INTEGER NOT NULL,
            request_status BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON DELETE CASCADE,
            FOREIGN KEY (book_instance_id) REFERENCES book_instances(book_instance_id) ON DELETE CASCADE,
            FOREIGN KEY (journal_id) REFERENCES journals(journal_id) ON DELETE CASCADE
        )
    """)

    # Таблица штрафов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fines (
            fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            amount REAL NOT NULL,
            status BOOLEAN NOT NULL DEFAULT 0,
            fine_date TEXT NOT NULL,
            loan_id INTEGER NOT NULL,
            FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON DELETE CASCADE,
            FOREIGN KEY (loan_id) REFERENCES loans(loan_id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def join_queue_window():
    queue_window = Toplevel(root)
    configure_theme(queue_window)
    queue_window.title("Запись в очередь")
    queue_window.geometry("400x300")

    # Выбор типа экземпляра (книга или журнал)
    Label(queue_window, text="Выберите тип экземпляра:").pack(pady=5)
    instance_type = StringVar(value="book")
    Radiobutton(queue_window, text="Книга", variable=instance_type, value="book").pack(pady=5)
    Radiobutton(queue_window, text="Журнал", variable=instance_type, value="journal").pack(pady=5)

    # Поле для ввода ID экземпляра
    Label(queue_window, text="Введите ID экземпляра:").pack(pady=5)
    instance_id_entry = Entry(queue_window)
    instance_id_entry.pack(pady=5)

    # Поле для ввода ID читателя
    Label(queue_window, text="Введите ID читателя:").pack(pady=5)
    reader_id_entry = Entry(queue_window)
    reader_id_entry.pack(pady=5)

    # Функция для добавления в очередь
    def add_to_queue():
        instance_id = instance_id_entry.get().strip()
        reader_id = reader_id_entry.get().strip()

        if not instance_id or not reader_id:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        if not instance_id.isdigit() or not reader_id.isdigit():
            messagebox.showerror("Ошибка", "ID экземпляра и ID читателя должны быть числами.")
            return

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        try:
            # Проверяем существование экземпляра книги или журнала
            if instance_type.get() == "book":
                cursor.execute("SELECT 1 FROM book_instances WHERE book_instance_id = ?", (instance_id,))
            elif instance_type.get() == "journal":
                cursor.execute("SELECT 1 FROM journals WHERE journal_id = ?", (instance_id,))
            else:
                raise ValueError("Неверный тип экземпляра.")

            if not cursor.fetchone():
                messagebox.showerror("Ошибка", "Экземпляр с указанным ID не найден.")
                return

            # Определяем текущее количество людей в очереди
            if instance_type.get() == "book":
                cursor.execute("""
                    SELECT COUNT(*) FROM queues WHERE book_instance_id = ?
                """, (instance_id,))
            elif instance_type.get() == "journal":
                cursor.execute("""
                    SELECT COUNT(*) FROM queues WHERE journal_id = ?
                """, (instance_id,))
            
            queue_count = cursor.fetchone()[0]
            new_position = queue_count + 1

            # Добавляем читателя в очередь
            if instance_type.get() == "book":
                cursor.execute("""
                    INSERT INTO queues (reader_id, book_instance_id, journal_id, queue_position, request_status)
                    VALUES (?, ?, NULL, ?, 0)
                """, (reader_id, instance_id, new_position))
            elif instance_type.get() == "journal":
                cursor.execute("""
                    INSERT INTO queues (reader_id, book_instance_id, journal_id, queue_position, request_status)
                    VALUES (?, NULL, ?, ?, 0)
                """, (reader_id, instance_id, new_position))

            conn.commit()
            messagebox.showinfo("Успех", f"Читатель добавлен в очередь на позицию {new_position}.")
            queue_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить в очередь: {e}")
        finally:
            conn.close()

    # Кнопка добавления в очередь
    Button(queue_window, text="Встать в очередь", command=add_to_queue).pack(pady=20)

    # Кнопка закрытия окна
    Button(queue_window, text="Закрыть", command=queue_window.destroy).pack(pady=5)


def show_queue_window():
    queue_window = Toplevel(root)
    configure_theme(queue_window)
    queue_window.title("Очередь")
    queue_window.geometry("500x400")

    # Выбор типа экземпляра (книга или журнал)
    Label(queue_window, text="Выберите тип экземпляра:").pack(pady=5)
    instance_type = StringVar(value="book")
    Radiobutton(queue_window, text="Книга", variable=instance_type, value="book").pack(pady=5)
    Radiobutton(queue_window, text="Журнал", variable=instance_type, value="journal").pack(pady=5)

    # Поле для ввода ID экземпляра
    Label(queue_window, text="Введите ID экземпляра:").pack(pady=5)
    instance_id_entry = Entry(queue_window)
    instance_id_entry.pack(pady=5)

    # Функция для отображения очереди
    def display_queue():
        instance_id = instance_id_entry.get().strip()

        if not instance_id.isdigit():
            messagebox.showerror("Ошибка", "ID экземпляра должен быть числом.")
            return

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        try:
            if instance_type.get() == "book":
                cursor.execute("""
                    SELECT queue_position, reader_id, request_status
                    FROM queues
                    WHERE book_instance_id = ?
                    ORDER BY queue_position
                """, (instance_id,))
            elif instance_type.get() == "journal":
                cursor.execute("""
                    SELECT queue_position, reader_id, request_status
                    FROM queues
                    WHERE journal_id = ?
                    ORDER BY queue_position
                """, (instance_id,))
            else:
                raise ValueError("Неверный тип экземпляра.")

            queue = cursor.fetchall()

            # Очистка старых результатов (если есть)
            for widget in queue_window.pack_slaves():
                if isinstance(widget, Listbox):
                    widget.destroy()

            if queue:
                Label(queue_window, text="Очередь:").pack(pady=10)

                # Отображение очереди в Listbox
                queue_listbox = Listbox(queue_window, width=60, height=15)
                queue_listbox.pack(pady=10)

                for position, reader_id, status in queue:
                    status_text = "Обработана" if status else "В ожидании"
                    queue_listbox.insert(
                        END, f"Позиция: {position}, ID Читателя: {reader_id}, Статус: {status_text}"
                    )
            else:
                messagebox.showinfo("Очередь", "Очередь отсутствует.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить очередь: {e}")
        finally:
            conn.close()

    # Кнопка для отображения очереди
    Button(queue_window, text="Показать очередь", command=display_queue).pack(pady=10)

    # Кнопка закрытия окна
    Button(queue_window, text="Закрыть", command=queue_window.destroy).pack(pady=5)


def issue_window():
    issue_window = Toplevel(root)
    configure_theme(issue_window)
    issue_window.title("Выдача экземпляра")
    issue_window.geometry("400x400")

    # Выбор: книга или журнал
    selection_label = Label(issue_window, text="Выберите тип выдачи:")
    selection_label.pack(pady=5)

    issue_type = StringVar(value="book")
    Radiobutton(issue_window, text="Книга", variable=issue_type, value="book").pack(pady=10)
    Radiobutton(issue_window, text="Журнал", variable=issue_type, value="journal").pack(pady=10)

    # Поля для ввода
    Label(issue_window, text="ID экземпляра (книга) / ID журнала:").pack(pady=5)
    instance_id_entry = Entry(issue_window)
    instance_id_entry.pack(pady=5)

    Label(issue_window, text="ID читателя:").pack(pady=5)
    reader_id_entry = Entry(issue_window)
    reader_id_entry.pack(pady=5)

    Label(issue_window, text="Срок возврата (ГГГГ-ММ-ДД):").pack(pady=5)
    due_date_entry = Entry(issue_window)
    due_date_entry.pack(pady=5)

    # Функция сохранения данных
    def save_loan():
        instance_id = instance_id_entry.get().strip()
        reader_id = reader_id_entry.get().strip()
        due_date = due_date_entry.get().strip()
        is_book = issue_type.get() == "book"

        if not instance_id or not reader_id or not due_date:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        # Получение текущей даты
        issue_date = datetime.now().strftime("%Y-%m-%d")

        try:
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()

            if is_book:
                # Проверяем существование экземпляра книги
                cursor.execute("SELECT 1 FROM book_instances WHERE book_instance_id = ?", (instance_id,))
            else:
                # Проверяем существование журнала
                cursor.execute("SELECT 1 FROM journals WHERE journal_id = ?", (instance_id,))
            
            if not cursor.fetchone():
                messagebox.showerror("Ошибка", "Экземпляр с указанным ID не найден.")
                return

            # Вставка данных в таблицу loans
            cursor.execute("""
                INSERT INTO loans (reader_id, book_instance_id, journal_id, issue_date, due_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                reader_id,
                instance_id if is_book else None,
                None if is_book else instance_id,
                issue_date,
                due_date,
            ))
            conn.commit()

            messagebox.showinfo("Успех", "Выдача успешно зарегистрирована.")
            issue_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить выдачу: {e}")
        finally:
            conn.close()

    # Кнопка сохранения
    Button(issue_window, text="Зарегистрировать выдачу", command=save_loan).pack(pady=20)



def show_instances(event, results_listbox):
    # Получаем выделенный элемент
    selection = results_listbox.curselection()
    if not selection:
        return

    selected_item = results_listbox.get(selection[0])

    # Определяем, что выбрано: книга или журнал
    if "Зависит" in selected_item:  # Проверка для книги
        item_id = selected_item.split(",")[0].strip()  # Получаем id книги
        is_book = True
    else:  # Если не книга, то это журнал
        item_id = selected_item.split(",")[0].strip()  # Получаем id журнала
        is_book = False

    # Создаем окно для отображения экземпляров
    instances_window = Toplevel(root)
    instances_window.title("Экземпляры")
    instances_window.geometry("400x300")

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    try:
        if is_book:
            # Для книги - получаем экземпляры книги
            cursor.execute("""
                SELECT book_instances.book_instance_id, book_instances.storage_shelf, book_instances.publisher, book_instances.year, book_instances.availability
                FROM book_instances
                WHERE book_instances.book_id = ?
            """, (item_id,))
        else:
            # Для журнала - получаем экземпляры журнала
            cursor.execute("""
                SELECT journals.journal_id, journals.storage_shelf, journals.title, journals.issue, journals.publication_date, journals.section, journals.availability
                FROM journals
                WHERE journals.journal_id = ?
            """, (item_id,))
        
        instances = cursor.fetchall()

        # Если экземпляры найдены
        if instances:
            instances_listbox = Listbox(instances_window, width=60, height=15)
            instances_listbox.pack(pady=10)

            for instance in instances:
                if is_book:
                    # Формат для книги
                    instance_id, storage_shelf, publisher, year, availability = instance  # исправили распаковку
                    in_stock = "Доступен" if availability else "Занят"
                    instances_listbox.insert(
                        END, f"ID экземпляра: {instance_id}, Код хранения: {storage_shelf}, Доступность: {in_stock}, Издательство: {publisher}, Год издания: {year}"
                    )
                else:
                    # Формат для журнала
                    instance_id, storage_shelf, title, issue, publication_date, section, availability = instance  # исправили распаковку
                    in_stock = "Доступен" if availability else "Занят"
                    instances_listbox.insert(
                        END, f"ID экземпляра: {instance_id}, Код хранения: {storage_shelf}, Доступность: {in_stock}, Номер выпуска: {issue}, Дата публикации: {publication_date}, Тематика: {section}"
                    )
        else:
            Label(instances_window, text="Нет доступных экземпляров.").pack(pady=10)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    finally:
        conn.close()

def search_items(search_window):
    def execute_search():
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        search_query = search_entry.get().strip()
        search_criteria = criteria_var.get()

        if not search_query:
            messagebox.showerror("Ошибка", "Введите запрос для поиска.")
            return

        # Определяем SQL-запрос в зависимости от критерия
        if search_criteria == "Название":
            query = """
                SELECT book_id, NULL as journal_id, title, author, section, NULL as year
                FROM books
                WHERE title LIKE ?
                UNION ALL
                SELECT NULL as book_id, journal_id, title, NULL as author, section, publication_date as year
                FROM journals
                WHERE title LIKE ?
            """
            params = (f"%{search_query}%", f"%{search_query}%")
        elif search_criteria == "Автор":
            query = """
                SELECT book_id, NULL as journal_id, title, author, section, NULL as year
                FROM books
                WHERE author LIKE ?
            """
            params = (f"%{search_query}%",)
        elif search_criteria == "Тематика":
            query = """
                SELECT book_id, NULL as journal_id, title, author, section, NULL as year
                FROM books
                WHERE section LIKE ?
                UNION ALL
                SELECT NULL as book_id, journal_id, title, NULL as author, section, publication_date as year
                FROM journals
                WHERE section LIKE ?
            """
            params = (f"%{search_query}%", f"%{search_query}%")
        elif search_criteria == "Год издания":
            query = """
                SELECT NULL as book_id, journal_id, title, NULL as author, section, publication_date as year
                FROM journals
                WHERE publication_date LIKE ?
            """
            params = (f"{search_query}%",)  # Добавляем "%" для поиска по году.
        else:
            messagebox.showerror("Ошибка", "Выберите критерий поиска.")
            return

        try:
            # Выполнение запроса
            cursor.execute(query, params)
            results = cursor.fetchall()

            # Очистка и обновление результатов
            results_listbox.delete(0, END)
            if results:
                for result in results:
                    book_id, journal_id, title, author, section, year = result
                    author = author if author else "Не указано"
                    year = year if year else "Зависит от экземпляра"
                    identifier = f"{book_id}" if book_id else f"{journal_id}"
                    results_listbox.insert(
                        END,
                        f"{identifier}, Название: {title}, Автор: {author}, Тематика: {section}, Год: {year}"
                    )
            else:
                results_listbox.insert(END, "Результаты не найдены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        finally:
            conn.close()

    
    # Создание окна поиска
    search_window.title("Поиск книг и журналов")
    search_window.geometry("1000x1000")

    # Поле ввода для поиска
    search_label = Label(search_window, text="Введите запрос:")
    search_label.pack(pady=5)
    search_entry = Entry(search_window, width=50)
    search_entry.pack(pady=5)

    # Выбор критерия поиска
    criteria_var = StringVar(value="Название")  # Критерий по умолчанию
    criteria_label = Label(search_window, text="Выберите критерий:")
    criteria_label.pack(pady=5)

    criteria_dropdown = OptionMenu(
        search_window, criteria_var, "Название", "Автор", "Тематика", "Год издания"
    )
    criteria_dropdown.pack(pady=5)

    # Кнопка выполнения поиска
    search_button = Button(search_window, text="Искать", command=execute_search)
    search_button.pack(pady=10)

    # Поле вывода результатов
    results_listbox = Listbox(search_window, width=80, height=15)
    results_listbox.bind("<Double-Button-1>", lambda event: show_instances(event, results_listbox))
    results_listbox.pack(pady=10)

    # Кнопка для закрытия окна поиска
    close_button = Button(search_window, text="Закрыть", command=search_window.destroy)
    close_button.pack(pady=10)



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

            else:
                open_user_dashboard(reader_id)
                
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
    def update_user_information():
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Получение имени, фамилии, количества активных долгов
        cursor.execute("SELECT first_name, last_name, active_debts FROM readers WHERE reader_id = ?", (reader_id,))
        reader_info = cursor.fetchone()

        if reader_info:
            first_name, last_name, active_debts = reader_info

            # Обновление текста меток
            name_label.configure(text=f"Имя: {first_name} {last_name}")
            debts_label.configure(text=f"Активные долги: {'Есть' if active_debts > 0 else 'Нет'}")

            # Обработка долгов
            if active_debts > 0:
                cursor.execute("""
                    SELECT 
                        loans.book_instance_id, 
                        loans.journal_id, 
                        loans.issue_date, 
                        loans.due_date, 
                        books.title AS book_title, 
                        journals.title AS journal_title
                    FROM loans
                    LEFT JOIN book_instances ON loans.book_instance_id = book_instances.book_instance_id
                    LEFT JOIN books ON book_instances.book_id = books.book_id
                    LEFT JOIN journals ON loans.journal_id = journals.journal_id
                    WHERE loans.reader_id = ? AND (julianday('now') - julianday(loans.due_date)) > 0
                """, (reader_id,))
                active_loans = cursor.fetchall()

                # Если `debts_listbox` еще не создан, создаем его
                if not hasattr(update_user_information, "debts_listbox"):
                    update_user_information.debts_listbox = Listbox(user_window, width=80, height=10)
                    update_user_information.debts_listbox.pack(pady=5)

                # Очистка списка долгов перед обновлением
                update_user_information.debts_listbox.delete(0, END)

                if active_loans:
                    for loan in active_loans:
                        book_instance_id, journal_id, issue_date, due_date, book_title, journal_title = loan
                        if book_instance_id:
                            item_title = f"Книга: {book_title} | ID экземпляра: {book_instance_id}"
                        else:
                            item_title = f"Журнал: {journal_title} | ID: {journal_id}"

                        update_user_information.debts_listbox.insert(
                            END, f"{item_title} | Выдана: {issue_date} | Срок: {due_date}"
                        )
                else:
                    # Если долгов нет, удаляем debts_listbox
                    if hasattr(update_user_information, "debts_listbox"):
                        update_user_information.debts_listbox.destroy()
                        del update_user_information.debts_listbox
            else:
                # Удаляем debts_listbox, если он существует
                if hasattr(update_user_information, "debts_listbox"):
                    update_user_information.debts_listbox.destroy()
                    del update_user_information.debts_listbox

            # Обработка штрафов
            cursor.execute("SELECT reason, amount, fine_date, status FROM fines WHERE reader_id = ?", (reader_id,))
            fines = cursor.fetchall()

            # Обновление текста метки штрафов
            fines_label.configure(text=f"Активные штрафы: {len(fines)}")

            if fines:
                # Если `fines_listbox` еще не создан, создаем его
                if not hasattr(update_user_information, "fines_listbox"):
                    update_user_information.fines_listbox = Listbox(user_window, width=80, height=10)
                    update_user_information.fines_listbox.pack(pady=5)

                # Очистка списка штрафов перед обновлением
                update_user_information.fines_listbox.delete(0, END)

                for fine in fines:
                    reason, amount, fine_date, status = fine
                    status_text = "Оплачен" if status == "Оплачен" else "Неоплачен"
                    update_user_information.fines_listbox.insert(
                        END, f"Штраф: {reason} | Сумма: {amount:.2f} | Дата: {fine_date} | Статус: {status_text}"
                    )
            else:
                # Удаляем fines_listbox, если он существует
                if hasattr(update_user_information, "fines_listbox"):
                    update_user_information.fines_listbox.destroy()
                    del update_user_information.fines_listbox
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить информацию о пользователе.")
        
        conn.close()

    # Создание окна личного кабинета пользователя
    user_window = Toplevel(root)
    configure_theme(user_window)
    user_window.title("Личный кабинет")
    user_window.geometry("400x1000")

    # Метки для отображения информации
    name_label = create_rounded_label(user_window, text="Загрузка...")  # Заглушка до обновления данных
    name_label.pack(pady=5)
    debts_label = create_rounded_label(user_window, text="Загрузка...")  # Заглушка до обновления данных
    debts_label.pack(pady=5)
    fines_label = create_rounded_label(user_window, text="Загрузка...")  # Заглушка до обновления данных
    fines_label.pack(pady=5)
    search_button = create_rounded_button(user_window, text="Поиск книг/журналов", command=lambda: search_items(Toplevel(user_window)))
    search_button.pack(pady=10)
    create_rounded_button(user_window, text="Просмотреть очередь", command=show_queue_window).pack(pady=10)
    create_rounded_button(user_window, text="Записаться в очередь", command=join_queue_window).pack(pady=10)


    # Обновление информации о пользователе
    update_user_information()

    # Кнопка для выхода
    create_rounded_button(user_window, text="Выйти", command=user_window.destroy).pack(pady=5)


def open_admin_dashboard(reader_id):
    admin_window = Toplevel(root)
    configure_theme(admin_window)
    admin_window.title("Личный кабинет")
    admin_window.geometry("400x1000")

    search_button = create_rounded_button(admin_window, text="Поиск книг/журналов", command=lambda: search_items(Toplevel(admin_window)))
    search_button.pack(pady=10)
    create_rounded_button(admin_window, text="Выдача книги", command=issue_window).pack(pady=10)
    create_rounded_button(admin_window, text="Просмотреть очередь", command=show_queue_window).pack(pady=10)
    # Кнопка для выхода
    create_rounded_button(admin_window, text="Выйти", command=admin_window.destroy).pack(pady=5)
    

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

'''
Добавить:

Встать в очередь на литературу


'''