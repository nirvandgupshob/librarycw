import sqlite3
from tkinter import Tk, Toplevel, Label, Listbox, messagebox, END, StringVar, OptionMenu, Entry, Button, Radiobutton, Frame
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


def show_statistics_window():
    window = Toplevel(root)
    configure_theme(window)
    window.title("Глобальная статистика библиотеки")
    window.geometry("400x400")

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM book_instances")
        total_books = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM readers WHERE role = 'Читатель'")
        total_readers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM journals")
        total_journals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM book_instances WHERE availability = 1")
        available_books = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM book_instances WHERE availability = 0")
        reserved_books = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM journals WHERE availability = 0")
        reserved_journals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM journals WHERE availability = 1")
        available_journals = cursor.fetchone()[0]



        # Вывод статистики на экран
        Label(window, text=f"Общее количество книг: {total_books}", font=("Arial", 12)).pack(pady=5)
        Label(window, text=f"Общее количество журналов: {total_journals}", font=("Arial", 12)).pack(pady=5)
        Label(window, text=f"Доступных книг: {available_books}", font=("Arial", 12)).pack(pady=5)
        Label(window, text=f"Забронированных книг: {reserved_books}", font=("Arial", 12)).pack(pady=5)
        Label(window, text=f"Доступных журналов: {available_journals}", font=("Arial", 12)).pack(pady=5)
        Label(window, text=f"Забронированных журналов: {reserved_journals}", font=("Arial", 12)).pack(pady=5)
        Label(window, text=f"Общее количество читателей: {total_readers}", font=("Arial", 12)).pack(pady=5)
        # Дополнительная информация, например, общее количество экземпляров книг
        # можно добавить дополнительные статистические данные в зависимости от потребностей.
        
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Не удалось получить статистику: {e}")
    finally:
        conn.close()

    # Кнопка для закрытия окна
    Button(window, text="Закрыть", command=window.destroy).pack(pady=20)

def delete_item_window():
    window = Toplevel(root)
    configure_theme(window)
    window.title("Удаление книги, журнала или экземпляра книги")
    window.geometry("400x250")

    # Выбор типа элемента (книга, журнал или экземпляр книги)
    Label(window, text="Выберите тип элемента для удаления:").pack(pady=5)
    item_type = StringVar(value="book")
    Radiobutton(window, text="Книга", variable=item_type, value="book").pack()
    Radiobutton(window, text="Журнал", variable=item_type, value="journal").pack()
    Radiobutton(window, text="Экземпляр книги", variable=item_type, value="book_instance").pack()

    # Поле для ввода ID
    Label(window, text="Введите ID элемента для удаления:").pack(pady=5)
    item_id_entry = Entry(window)
    item_id_entry.pack()

    # Функция для удаления элемента из базы данных
    def delete_item():
        item_id = item_id_entry.get().strip()

        if not item_id:
            messagebox.showerror("Ошибка", "Введите ID элемента для удаления!")
            return

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        try:
            # Удаление книги
            if item_type.get() == "book":
                # Сначала удаляем экземпляры книги, если они есть
                cursor.execute("""
                    DELETE FROM book_instances WHERE book_id = ?
                """, (item_id,))
                # Затем удаляем саму книгу из books
                cursor.execute("""
                    DELETE FROM books WHERE book_id = ?
                """, (item_id,))
            
            # Удаление журнала
            elif item_type.get() == "journal":
                cursor.execute("""
                    DELETE FROM journals WHERE journal_id = ?
                """, (item_id,))
            
            # Удаление экземпляра книги
            elif item_type.get() == "book_instance":
                cursor.execute("""
                    DELETE FROM book_instances WHERE book_instance_id = ?
                """, (item_id,))

            conn.commit()
            messagebox.showinfo("Успех", "Элемент успешно удален из базы!")
            window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить элемент: {e}")
        finally:
            conn.close()

    # Кнопка для удаления
    Button(window, text="Удалить", command=delete_item).pack(pady=20)
    Button(window, text="Закрыть", command=window.destroy).pack()


def register_reader_window():
    window = Toplevel(root)
    configure_theme(window)
    window.title("Регистрация нового читателя")
    window.geometry("400x600")

    # Поля для ввода данных
    Label(window, text="Имя:").pack(pady=5)
    first_name_entry = Entry(window)
    first_name_entry.pack()

    Label(window, text="Фамилия:").pack(pady=5)
    last_name_entry = Entry(window)
    last_name_entry.pack()

    Label(window, text="Номер телефона:").pack(pady=5)
    phone_number_entry = Entry(window)
    phone_number_entry.pack()

    Label(window, text="Пароль:").pack(pady=5)
    password_entry = Entry(window, show="*")
    password_entry.pack()

    # Функция для сохранения читателя в базу данных
    def register_reader():
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        phone_number = phone_number_entry.get().strip()
        password = password_entry.get().strip()

        if not all([first_name, last_name, phone_number, password]):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверяем уникальность номера телефона
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO readers (first_name, last_name, phone_number, password, role)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, phone_number, password, "Читатель"))
            conn.commit()
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Этот номер телефона уже зарегистрирован!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось зарегистрировать читателя: {e}")
        finally:
            conn.close()

    # Кнопки для регистрации и закрытия окна
    Button(window, text="Зарегистрировать", command=register_reader).pack(pady=20)
    Button(window, text="Закрыть", command=window.destroy).pack()


def add_item_window():
    window = Toplevel(root)
    configure_theme(window)
    window.title("Добавление книги, журнала или экземпляра книги")
    window.geometry("400x1000")

    # Выбор типа элемента (книга, журнал или экземпляр книги)
    Label(window, text="Выберите тип элемента:").pack(pady=5)
    item_type = StringVar(value="book")
    Radiobutton(window, text="Книга", variable=item_type, value="book", command=lambda: show_fields("book")).pack()
    Radiobutton(window, text="Журнал", variable=item_type, value="journal", command=lambda: show_fields("journal")).pack()
    Radiobutton(window, text="Экземпляр книги", variable=item_type, value="book_instance", command=lambda: show_fields("book_instance")).pack()

    # Фрейм для полей ввода
    fields_frame = Frame(window)
    fields_frame.pack(pady=10)

    # Поля ввода
    fields = {}

    def show_fields(item_type):
        # Очистка предыдущих полей
        for widget in fields_frame.winfo_children():
            widget.destroy()

        fields.clear()

        if item_type == "book":
            Label(fields_frame, text="Название:").pack(pady=5)
            fields["title"] = Entry(fields_frame)
            fields["title"].pack()

            Label(fields_frame, text="Автор:").pack(pady=5)
            fields["author"] = Entry(fields_frame)
            fields["author"].pack()

            Label(fields_frame, text="Раздел:").pack(pady=5)
            fields["section"] = Entry(fields_frame)
            fields["section"].pack()

        elif item_type == "journal":
            Label(fields_frame, text="Название:").pack(pady=5)
            fields["title"] = Entry(fields_frame)
            fields["title"].pack()

            Label(fields_frame, text="Выпуск:").pack(pady=5)
            fields["issue"] = Entry(fields_frame)
            fields["issue"].pack()

            Label(fields_frame, text="Дата публикации (YYYY-MM-DD):").pack(pady=5)
            fields["publication_date"] = Entry(fields_frame)
            fields["publication_date"].pack()

            Label(fields_frame, text="Раздел:").pack(pady=5)
            fields["section"] = Entry(fields_frame)
            fields["section"].pack()

            Label(fields_frame, text="Код хранения:").pack(pady=5)
            fields["storage_shelf"] = Entry(fields_frame)
            fields["storage_shelf"].pack()

        elif item_type == "book_instance":
            Label(fields_frame, text="ID книги:").pack(pady=5)
            fields["book_id"] = Entry(fields_frame)
            fields["book_id"].pack()

            Label(fields_frame, text="Место хранения:").pack(pady=5)
            fields["storage_shelf"] = Entry(fields_frame)
            fields["storage_shelf"].pack()

            Label(fields_frame, text="Издатель:").pack(pady=5)
            fields["publisher"] = Entry(fields_frame)
            fields["publisher"].pack()

            Label(fields_frame, text="Год издания:").pack(pady=5)
            fields["year"] = Entry(fields_frame)
            fields["year"].pack()

    # Функция для добавления данных в базу
    def add_to_database():
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        try:
            if item_type.get() == "book":
                title = fields["title"].get().strip()
                author = fields["author"].get().strip()
                section = fields["section"].get().strip()

                if not all([title, author, section]):
                    raise ValueError("Заполните все поля для книги!")

                cursor.execute("""
                    INSERT INTO books (title, author, section)
                    VALUES (?, ?, ?)
                """, (title, author, section))

            elif item_type.get() == "journal":
                title = fields["title"].get().strip()
                issue = fields["issue"].get().strip()
                publication_date = fields["publication_date"].get().strip()
                section = fields["section"].get().strip()
                storage_shelf = fields["storage_shelf"].get().strip()

                if not all([title, issue, publication_date, section, storage_shelf]):
                    raise ValueError("Заполните все поля для журнала!")

                cursor.execute("""
                    INSERT INTO journals (title, issue, publication_date, section, availability, storage_shelf)
                    VALUES (?, ?, ?, ?, 1, ?)
                """, (title, issue, publication_date, section, storage_shelf))

            elif item_type.get() == "book_instance":
                book_id = fields["book_id"].get().strip()
                storage_shelf = fields["storage_shelf"].get().strip()
                publisher = fields["publisher"].get().strip()
                year = fields["year"].get().strip()

                if not all([book_id, storage_shelf, publisher, year]):
                    raise ValueError("Заполните все поля для экземпляра книги!")

                cursor.execute("""
                    INSERT INTO book_instances (book_id, storage_shelf, publisher, year, availability)
                    VALUES (?, ?, ?, ?, 1)
                """, (book_id, storage_shelf, publisher, int(year)))

            conn.commit()
            messagebox.showinfo("Успех", "Элемент успешно добавлен в базу!")
            window.destroy()
        except (ValueError, sqlite3.Error) as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить элемент: {e}")
        finally:
            conn.close()

    # Кнопка для добавления
    Button(window, text="Добавить", command=add_to_database).pack(pady=20)
    Button(window, text="Закрыть", command=window.destroy).pack()


def pay_fine_window():
    """
    Открывает окно для погашения штрафов читателя.
    """
    pay_fine_main_window = Toplevel(root)
    configure_theme(pay_fine_main_window)
    pay_fine_main_window.title("Погашение штрафов")
    pay_fine_main_window.geometry("400x400")

    # Поле для ввода ID читателя
    Label(pay_fine_main_window, text="Введите ID читателя:").pack(pady=5)
    reader_id_entry = Entry(pay_fine_main_window)
    reader_id_entry.pack(pady=5)

    # Listbox для отображения штрафов
    fines_listbox = Listbox(pay_fine_main_window, width=50, height=15)
    fines_listbox.pack(pady=10)

    # Функция для загрузки штрафов
    def load_fines():
        reader_id = reader_id_entry.get().strip()

        if not reader_id:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ID читателя.")
            return

        if not reader_id.isdigit():
            messagebox.showerror("Ошибка", "ID читателя должен быть целым числом.")
            return

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        try:
            # Проверка существования читателя
            cursor.execute("SELECT 1 FROM readers WHERE reader_id = ?", (reader_id,))
            if not cursor.fetchone():
                messagebox.showerror("Ошибка", "Читатель с указанным ID не найден.")
                return

            # Загрузка штрафов для указанного читателя
            cursor.execute("""
                SELECT fine_id, reason, amount, status, fine_date 
                FROM fines 
                WHERE reader_id = ? AND status = 0
            """, (reader_id,))
            fines = cursor.fetchall()

            fines_listbox.delete(0, END)  # Очистка списка
            if fines:
                for fine in fines:
                    fines_listbox.insert(END, f"ID: {fine[0]} | Причина: {fine[1]} | Сумма: {fine[2]} | Дата: {fine[4]}")
            else:
                messagebox.showinfo("Информация", "Нет неоплаченных штрафов для данного читателя.")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить штрафы: {e}")
        finally:
            conn.close()

    # Функция для погашения конкретного штрафа
    def pay_selected_fine(fine_id):
        def confirm_payment():
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE fines 
                    SET status = 1 
                    WHERE fine_id = ?
                """, (fine_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Штраф успешно погашен.")
                fine_payment_window.destroy()
                load_fines()  # Обновить список штрафов
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Не удалось погасить штраф: {e}")
            finally:
                conn.close()

        # Открытие окна для подтверждения погашения
        fine_payment_window = Toplevel(pay_fine_main_window)
        configure_theme(fine_payment_window)
        fine_payment_window.title("Подтверждение погашения штрафа")
        fine_payment_window.geometry("300x150")

        Label(fine_payment_window, text=f"Вы уверены, что хотите погасить штраф ID {fine_id}?").pack(pady=10)
        Button(fine_payment_window, text="Подтвердить", command=confirm_payment).pack(pady=5)
        Button(fine_payment_window, text="Отмена", command=fine_payment_window.destroy).pack(pady=5)

    # Обработка двойного клика на элементе списка
    def on_fine_double_click(event):
        selection = fines_listbox.curselection()
        if not selection:
            return

        selected_fine = fines_listbox.get(selection[0])
        fine_id = int(selected_fine.split('|')[0].split(':')[1].strip())  # Извлекаем ID штрафа
        pay_selected_fine(fine_id)

    fines_listbox.bind("<Double-1>", on_fine_double_click)

    # Кнопка загрузки штрафов
    Button(pay_fine_main_window, text="Загрузить штрафы", command=load_fines).pack(pady=10)

    # Кнопка для закрытия окна
    Button(pay_fine_main_window, text="Закрыть", command=pay_fine_main_window.destroy).pack(pady=5)


def open_fine_window():
   # Открывает окно для выписки штрафа читателю.
    fine_window = Toplevel(root)
    configure_theme(fine_window)
    fine_window.title("Выписать штраф")
    fine_window.geometry("400x400")

    # Поле для ввода ID читателя
    Label(fine_window, text="Введите ID читателя:").pack(pady=5)
    reader_id_entry = Entry(fine_window)
    reader_id_entry.pack(pady=5)

    # Поле для ввода ID выдачи (loan_id)
    Label(fine_window, text="Введите ID выдачи (loan_id):").pack(pady=5)
    loan_id_entry = Entry(fine_window)
    loan_id_entry.pack(pady=5)

    # Поле для ввода причины штрафа
    Label(fine_window, text="Введите причину штрафа:").pack(pady=5)
    reason_entry = Entry(fine_window)
    reason_entry.pack(pady=5)

    # Поле для ввода суммы штрафа
    Label(fine_window, text="Введите сумму штрафа:").pack(pady=5)
    amount_entry = Entry(fine_window)
    amount_entry.pack(pady=5)

    # Функция для добавления штрафа в базу данных
    def add_fine():
        reader_id = reader_id_entry.get().strip()
        loan_id = loan_id_entry.get().strip()
        reason = reason_entry.get().strip()
        amount = amount_entry.get().strip()

        # Проверка на заполнение полей
        if not reader_id or not loan_id or not reason or not amount:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Проверка на корректность суммы
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
            return

        # Проверка на целочисленные ID
        if not reader_id.isdigit() or not loan_id.isdigit():
            messagebox.showerror("Ошибка", "ID читателя и ID выдачи должны быть целыми числами.")
            return

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        try:
            # Проверка существования reader_id
            cursor.execute("SELECT 1 FROM readers WHERE reader_id = ?", (reader_id,))
            if not cursor.fetchone():
                messagebox.showerror("Ошибка", "Читатель с указанным ID не найден.")
                return

            # Проверка существования loan_id
            cursor.execute("SELECT 1 FROM loans WHERE loan_id = ?", (loan_id,))
            if not cursor.fetchone():
                messagebox.showerror("Ошибка", "Выдача с указанным ID не найдена.")
                return

            # Добавление штрафа в таблицу fines
            cursor.execute("""
                INSERT INTO fines (reader_id, loan_id, reason, amount, fine_date)
                VALUES (?, ?, ?, ?, DATE('now'))
            """, (reader_id, loan_id, reason, amount))
            conn.commit()

            messagebox.showinfo("Успех", "Штраф успешно выписан.")
            fine_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить штраф: {e}")
        finally:
            conn.close()

    # Кнопка для добавления штрафа
    Button(fine_window, text="Выписать штраф", command=add_fine).pack(pady=20)

    # Кнопка для закрытия окна
    Button(fine_window, text="Закрыть", command=fine_window.destroy).pack(pady=5)


def return_window():
    return_window = Toplevel(root)
    configure_theme(return_window)
    return_window.title("Возврат экземпляра")
    return_window.geometry("400x400")

    # Выбор: книга или журнал
    selection_label = Label(return_window, text="Выберите тип возврата:")
    selection_label.pack(pady=5)

    return_type = StringVar(value="book")
    Radiobutton(return_window, text="Книга", variable=return_type, value="book").pack(pady=10)
    Radiobutton(return_window, text="Журнал", variable=return_type, value="journal").pack(pady=10)

    # Поле для ввода ID
    Label(return_window, text="ID экземпляра (книга) / ID журнала:").pack(pady=5)
    instance_id_entry = Entry(return_window)
    instance_id_entry.pack(pady=5)

    # Функция возврата
    def process_return():
        instance_id = instance_id_entry.get().strip()
        is_book = return_type.get() == "book"

        if not instance_id:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ID экземпляра.")
            return

        # Получение текущей даты
        actual_date = datetime.now().strftime("%Y-%m-%d")

        try:
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()

            # Проверяем, есть ли активная выдача для указанного экземпляра
            if is_book:
                cursor.execute("""
                    SELECT loan_id FROM loans
                    WHERE book_instance_id = ? AND actual_date IS NULL
                """, (instance_id,))
            else:
                cursor.execute("""
                    SELECT loan_id FROM loans
                    WHERE journal_id = ? AND actual_date IS NULL
                """, (instance_id,))
            
            loan = cursor.fetchone()
            if not loan:
                messagebox.showerror("Ошибка", "Для этого экземпляра нет активной выдачи.")
                return

            loan_id = loan[0]

            # Обновляем дату возврата
            cursor.execute("""
                UPDATE loans
                SET actual_date = ?
                WHERE loan_id = ?
            """, (actual_date, loan_id))

            # Проверяем, есть ли очередь на этот экземпляр
            if is_book:
                cursor.execute("""
                    SELECT reader_id FROM queues
                    WHERE book_instance_id = ?
                    ORDER BY queue_position ASC LIMIT 1
                """, (instance_id,))
            else:
                cursor.execute("""
                    SELECT reader_id FROM queues
                    WHERE journal_id = ?
                    ORDER BY queue_position ASC LIMIT 1
                """, (instance_id,))
            
            first_in_queue = cursor.fetchone()

            if first_in_queue:
                reader_id = first_in_queue[0]

                # Получаем телефон читателя
                cursor.execute("""
                    SELECT phone_number FROM readers WHERE reader_id = ?
                """, (reader_id,))
                reader_info = cursor.fetchone()
                phone = reader_info[0] if reader_info else "не указан"

                messagebox.showinfo("Очередь", f"Первый в очереди: reader_id = {reader_id}, телефон = {phone}")
            else:
                # Если очереди нет, помечаем экземпляр как доступный
                if is_book:
                    cursor.execute("""
                        UPDATE book_instances
                        SET availability = 1
                        WHERE book_instance_id = ?
                    """, (instance_id,))
                else:
                    cursor.execute("""
                        UPDATE journals
                        SET availability = 1
                        WHERE journal_id = ?
                    """, (instance_id,))
            
            conn.commit()
            messagebox.showinfo("Успех", "Возврат успешно оформлен.")
            return_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось оформить возврат: {e}")
        finally:
            conn.close()

    # Кнопка для оформления возврата
    Button(return_window, text="Оформить возврат", command=process_return).pack(pady=20)


def join_queue_window(current_reader_id):

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

    # Функция для добавления в очередь
    def add_to_queue():
        instance_id = instance_id_entry.get().strip()

        if not instance_id:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните поле.")
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
                    INSERT INTO queues (reader_id, book_instance_id, journal_id, queue_position)
                    VALUES (?, ?, NULL, ?)
                """, (current_reader_id, instance_id, new_position))
            elif instance_type.get() == "journal":
                cursor.execute("""
                    INSERT INTO queues (reader_id, book_instance_id, journal_id, queue_position)
                    VALUES (?, NULL, ?, ?)
                """, (current_reader_id, instance_id, new_position))

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
                    SELECT queue_position, reader_id
                    FROM queues
                    WHERE book_instance_id = ?
                    ORDER BY queue_position
                """, (instance_id,))
            elif instance_type.get() == "journal":
                cursor.execute("""
                    SELECT queue_position, reader_id
                    FROM queues
                    WHERE journal_id = ?
                    ORDER BY queue_position
                """, (instance_id,))
            else:
                raise ValueError("Неверный тип экземпляра.")

            queue = cursor.fetchall()

            # Удаляем все виджеты с текстом "Очередь:" и Listbox
            for widget in queue_window.pack_slaves():
                if isinstance(widget, Label) and widget.cget("text") == "Очередь:":
                    widget.destroy()
                elif isinstance(widget, Listbox):
                    widget.destroy()

            if queue:
                Label(queue_window, text="Очередь:").pack(pady=10)

                # Отображение очереди в Listbox
                queue_listbox = Listbox(queue_window, width=60, height=15)
                queue_listbox.pack(pady=10)

                for position, reader_id in queue:
                    queue_listbox.insert(
                        END, f"Позиция: {position}, ID Читателя: {reader_id}"
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

            # Проверяем очередь на экземпляр
            if is_book:
                cursor.execute("""
                    SELECT reader_id FROM queues
                    WHERE book_instance_id = ?
                    ORDER BY queue_position ASC LIMIT 1
                """, (instance_id,))
            else:
                cursor.execute("""
                    SELECT reader_id FROM queues
                    WHERE journal_id = ?
                    ORDER BY queue_position ASC LIMIT 1
                """, (instance_id,))
            
            first_in_queue = cursor.fetchone()

            if first_in_queue:
                queue_reader_id = first_in_queue[0]

                # Проверяем, совпадает ли reader_id с первым в очереди
                if int(reader_id) != queue_reader_id:
                    messagebox.showerror(
                        "Ошибка", 
                        "На данный экземпляр есть очередь. Выдача возможна только первому в очереди."
                    )
                    return
                
                # Удаляем запись очереди первого читателя
                if is_book:
                    cursor.execute("""
                        DELETE FROM queues
                        WHERE book_instance_id = ? AND reader_id = ?
                    """, (instance_id, reader_id))
                else:
                    cursor.execute("""
                        DELETE FROM queues
                        WHERE journal_id = ? AND reader_id = ?
                    """, (instance_id, reader_id))
                
                # Сдвигаем очередь
                if is_book:
                    cursor.execute("""
                        UPDATE queues
                        SET queue_position = queue_position - 1
                        WHERE book_instance_id = ?
                    """, (instance_id,))
                else:
                    cursor.execute("""
                        UPDATE queues
                        SET queue_position = queue_position - 1
                        WHERE journal_id = ?
                    """, (instance_id,))

            else:
                # Проверяем доступность экземпляра, если очереди нет
                if is_book:
                    cursor.execute("""
                        SELECT availability FROM book_instances WHERE book_instance_id = ?
                    """, (instance_id,))
                else:
                    cursor.execute("""
                        SELECT availability FROM journals WHERE journal_id = ?
                    """, (instance_id,))
                
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Ошибка", "Экземпляр с указанным ID не найден.")
                    return

                availability = result[0]
                if not availability:
                    messagebox.showerror("Ошибка", "Этот экземпляр уже выдан.")
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

            # Обновление статуса доступности экземпляра
            if is_book:
                cursor.execute("""
                    UPDATE book_instances SET availability = 0 WHERE book_instance_id = ?
                """, (instance_id,))
            else:
                cursor.execute("""
                    UPDATE journals SET availability = 0 WHERE journal_id = ?
                """, (instance_id,))

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

        # Получение имени и фамилии пользователя
        cursor.execute("SELECT first_name, last_name FROM readers WHERE reader_id = ?", (reader_id,))
        reader_info = cursor.fetchone()

        if reader_info:
            first_name, last_name = reader_info

            # Обновление текста меток
            name_label.configure(text=f"Имя: {first_name} {last_name}")

            # Проверка долгов
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

            # Обновление долгов
            if active_loans:
                debts_label.configure(text="Активные долги: Есть")

                if not hasattr(update_user_information, "debts_listbox"):
                    update_user_information.debts_listbox = Listbox(user_window, width=80, height=10)
                    update_user_information.debts_listbox.pack(pady=5)

                update_user_information.debts_listbox.delete(0, END)
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
                debts_label.configure(text="Активные долги: Нет")
                if hasattr(update_user_information, "debts_listbox"):
                    update_user_information.debts_listbox.destroy()
                    del update_user_information.debts_listbox

            # Проверка штрафов
            cursor.execute("SELECT reason, amount, fine_date, status FROM fines WHERE reader_id = ?", (reader_id,))
            fines = cursor.fetchall()

            if fines:
                fines_label.configure(text=f"Активные штрафы: {len([fine for fine in fines if fine[3] == 0])}")

                if not hasattr(update_user_information, "fines_listbox"):
                    update_user_information.fines_listbox = Listbox(user_window, width=80, height=10)
                    update_user_information.fines_listbox.pack(pady=5)

                update_user_information.fines_listbox.delete(0, END)
                for fine in fines:
                    reason, amount, fine_date, status = fine
                    status_text = "Оплачен" if status else "Неоплачен"
                    update_user_information.fines_listbox.insert(
                        END, f"Штраф: {reason} | Сумма: {amount:.2f} | Дата: {fine_date} | Статус: {status_text}"
                    )
            else:
                fines_label.configure(text="Активные штрафы: Нет")
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
    user_window.geometry("400x800")

    # Метки для отображения информации
    name_label = create_rounded_label(user_window, text="Загрузка...")  # Заглушка до обновления данных
    name_label.pack(pady=5)
    debts_label = create_rounded_label(user_window, text="Загрузка...")  # Заглушка до обновления данных
    debts_label.pack(pady=5)
    fines_label = create_rounded_label(user_window, text="Загрузка...")  # Заглушка до обновления данных
    fines_label.pack(pady=5)

    # Дополнительные кнопки
    search_button = create_rounded_button(user_window, text="Поиск книг/журналов", command=lambda: search_items(Toplevel(user_window)))
    search_button.pack(pady=10)
    create_rounded_button(user_window, text="Просмотреть очередь", command=show_queue_window).pack(pady=10)
    create_rounded_button(user_window, text="Записаться в очередь", command=lambda: join_queue_window(reader_id)).pack(pady=10)

    # Обновление информации о пользователе
    update_user_information()

    # Кнопка для выхода
    create_rounded_button(user_window, text="Выйти", command=user_window.destroy).pack(pady=5)



def open_admin_dashboard(reader_id):
    admin_window = Toplevel(root)
    configure_theme(admin_window)
    admin_window.title("Меню библиотекаря")
    admin_window.geometry("400x1000")

    search_button = create_rounded_button(admin_window, text="Поиск книг/журналов", command=lambda: search_items(Toplevel(admin_window)))
    search_button.pack(pady=10)
    create_rounded_button(admin_window, text="Выдача литературы", command=issue_window).pack(pady=10)
    create_rounded_button(admin_window, text="Просмотреть очередь", command=show_queue_window).pack(pady=10)
    create_rounded_button(admin_window, text="Возврат литературы", command=return_window).pack(pady=10)
    create_rounded_button(admin_window, text="Выписать штраф", command=open_fine_window).pack(pady=10)
    create_rounded_button(admin_window, text="Погасить штраф", command=pay_fine_window).pack(pady=10)
    create_rounded_button(admin_window, text="Добавить книгу или журнал", command=add_item_window).pack(pady=10)
    create_rounded_button(admin_window, text="Зарегистрировать читателя", command=register_reader_window).pack(pady=10)
    create_rounded_button(admin_window, text="Удалить книгу или журнал", command=delete_item_window).pack(pady=10)
    create_rounded_button(admin_window, text="Статистика", command=show_statistics_window).pack(pady=10)
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
