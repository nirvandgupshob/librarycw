import sqlite3
def populate_test_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Добавление тестовых пользователей
    cursor.execute("""
        INSERT OR IGNORE INTO readers (reader_id, first_name, last_name, phone_number, active_debts, password, role)
        VALUES 
        (3, 'Иван', 'Иванов', '1234567890', 1, '123', 'Гость'),
        (4, 'Петр', 'Петров', '0987654321', 0, '123', 'Библиотекарь')
    """)

    # Добавление тестовых книг
    cursor.execute("""
        INSERT OR IGNORE INTO books (book_id, title, author, section)
        VALUES 
        (1, 'Программирование на Python', 'Гвидо ван Россум', 'Программирование'),
        (2, 'Введение в базы данных', 'К. Дейт', 'Базы данных'),
        (3, 'Алгоритмы и структуры данных', 'Роберт Седжвик', 'Алгоритмы')
    """)

    # Добавление тестовых экземпляров книг
    cursor.execute("""
        INSERT OR IGNORE INTO book_instances (book_instance_id, book_id, storage_shelf, publisher, year, availability, last_issue_date)
        VALUES 
        (1, 1, 'A1', 'Издательство А', 2020, 1, NULL),
        (2, 2, 'B2', 'Издательство Б', 2019, 0, '2024-01-10'),
        (3, 3, 'C3', 'Издательство В', 2021, 1, NULL)
    """)

    # Добавление тестовых журналов
    cursor.execute("""
        INSERT OR IGNORE INTO journals (journal_id, title, issue, publisher, publication_date, section)
        VALUES 
        (1, 'Научный вестник', '1(2024)', 'Издательство Наука', '2024-01-01', 'Наука'),
        (2, 'Технический журнал', '2(2023)', 'ТехИздат', '2023-12-01', 'Техника')
    """)

    # Добавление тестовых экземпляров журналов
    cursor.execute("""
        INSERT OR IGNORE INTO journal_instances (journal_instance_id, journal_id, availability, last_issue_date)
        VALUES 
        (1, 1, 1, NULL),
        (2, 2, 0, '2024-02-15')
    """)

    # Добавление тестовых выдач литературы
    cursor.execute("""
        INSERT OR IGNORE INTO loans (loan_id, reader_id, item_id, issue_date, due_date, return_period)
        VALUES 
        (1, 3, 1, '2024-03-01', '2024-03-15', 14),
        (2, 3, 2, '2024-02-01', '2024-02-15', 14)
    """)

    # Добавление тестовой очереди на литературу
    cursor.execute("""
        INSERT OR IGNORE INTO queues (queue_id, reader_id, item_id, queue_position, request_status)
        VALUES 
        (1, 3, 3, 1, 'В ожидании'),
        (2, 4, 3, 2, 'В ожидании')
    """)

    # Добавление тестовых штрафов
    cursor.execute("""
        INSERT OR IGNORE INTO fines (fine_id, reader_id, reason, amount, status, fine_date, related_loan_id)
        VALUES 
        (1, 3, 'Просрочка возврата книги', 100.0, 'Неоплачен', '2024-03-20', 2)
    """)

    conn.commit()
    conn.close()
    print("Тестовые данные успешно добавлены!")

populate_test_data()
