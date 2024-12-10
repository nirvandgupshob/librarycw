import sqlite3

def populate_test_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Добавляем читателей
    cursor.executemany("""
        INSERT INTO readers (first_name, last_name, phone_number, active_debts, password, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("Fenny", "Lirst", "1234567890", 0, "123", "Читатель"),
        ("Lenny", "First", "0987654321", 0, "123", "Библиотекарь"),
        ("Hit", "Vandal", "88005353535", 0, "123", "Читатель"),
    ])

    # Добавляем книги
    cursor.executemany("""
        INSERT INTO books (title, author, section)
        VALUES (?, ?, ?)
    """, [
        ("Программирование на Python", "Гвидо ван Россум", "Информатика"),
        ("Алгоритмы и структуры данных", "Никлаус Вирт", "Информатика"),
    ])

    # Добавляем экземпляры книг
    cursor.executemany("""
        INSERT INTO book_instances (book_id, storage_shelf, publisher, year, availability)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "A1", "O'Reilly", 2020, 0),  # Книга выдана
        (2, "B2", "MIT Press", 2018, 1),  # Книга доступна
    ])

    # Добавляем журналы
    cursor.executemany("""
        INSERT INTO journals (title, issue, publication_date, section, availability, storage_shelf)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("Научные исследования", "№4", "2023-05-01", "Наука", 0, "C3"),
    ])

    # Добавляем выдачи
    cursor.executemany("""
        INSERT INTO loans (reader_id, book_instance_id, journal_id, issue_date, due_date, actual_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, 1, None, "2024-12-01", "2024-12-15", None),  # Книга 1 выдана читателю 1
        (1, None, 1, "2024-12-01", "2024-12-15", None),
    ])

    # Добавляем очередь на журнал
    cursor.executemany("""
        INSERT INTO queues (reader_id, book_instance_id, journal_id, queue_position)
        VALUES (?, ?, ?, ?)
    """, [
        (3, None, 1, 1),  # Читатель 3 в очереди на журнал 1
    ])

    conn.commit()
    conn.close()

# populate_test_data()
def fines():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO fines (reader_id, reason, amount, fine_date, loan_id)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "по приколу", 100, "2024-07-07", 1),
    ])

    conn.commit()
    conn.close()

fines()

