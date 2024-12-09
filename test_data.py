import sqlite3

def populate_test_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Добавление тестовых читателей
    cursor.execute("""
        INSERT OR IGNORE INTO readers (first_name, last_name, phone_number, active_debts, password, role) VALUES
        ('Genadiy', 'Pivovarov', '89965476893', 0, '123', 'Гость'),
        ('Lenny', 'First', '88005353535', 0, '123', 'Библиотекарь'),
        ('Иван', 'Иванов', '1234567890', 1, '123', 'Гость'),
        ('Петр', 'Петров', '0987654321', 0, '123', 'Библиотекарь')
    """)

    # Добавление тестовых книг
    cursor.execute("""
        INSERT OR IGNORE INTO books (title, author, section) VALUES
        ('Программирование на Python', 'Гвидо ван Россум', 'Программирование'),
        ('Введение в базы данных', 'К. Дейт', 'Базы данных'),
        ('Алгоритмы и структуры данных', 'Роберт Седжвик', 'Алгоритмы')
    """)

    # Добавление тестовых экземпляров книг
    cursor.execute("""
        INSERT OR IGNORE INTO book_instances (book_id, storage_shelf, publisher, year, availability) VALUES
        (1, 'A1', 'Издательство А', 2020, 1),
        (2, 'B2', 'Издательство Б', 2019, 0),
        (3, 'C3', 'Издательство В', 2021, 1)
    """)

    # Добавление тестовых журналов
    cursor.execute("""
        INSERT OR IGNORE INTO journals (title, issue, publication_date, section, availability, storage_shelf) VALUES
        ('Научный вестник', '1(2024)', '2024-01-01', 'Наука', 1, 'D1'),
        ('Технический журнал', '2(2023)', '2023-12-01', 'Техника', 0, 'E2')
    """)

    # Добавление тестовых выдач литературы
    cursor.execute("""
        INSERT OR IGNORE INTO loans (reader_id, book_instance_id, journal_id, issue_date, due_date, actual_date) VALUES
        (3, 1, NULL, '2024-03-01', '2024-03-15', NULL),
        (3, NULL, 2, '2024-02-01', '2024-02-15', '2024-02-16')
    """)

    # Добавление тестовой очереди на литературу
    cursor.execute("""
        INSERT OR IGNORE INTO queues (reader_id, book_instance_id, journal_id, queue_position, request_status) VALUES
        (3, 3, NULL, 1, 0),
        (4, 3, NULL, 2, 0),
        (3, NULL, 1, 1, 0)
    """)

    # Добавление тестовых штрафов
    cursor.execute("""
        INSERT OR IGNORE INTO fines (reader_id, reason, amount, status, fine_date, loan_id) VALUES
        (3, 'Просрочка возврата книги', 100.0, 0, '2024-03-20', 2)
    """)

    conn.commit()
    conn.close()
    print("Тестовые данные успешно добавлены!")

# populate_test_data()
def second_amendment():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO loans (reader_id, book_instance_id, issue_date, due_date)
    VALUES (?, ?, ?, ?)
""", (1, 3, '2024-10-06', '2024-10-20'))
    conn.commit()
    conn.close()

second_amendment()
