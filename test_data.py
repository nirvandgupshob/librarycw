import sqlite3

def populate_test_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Добавляем читателей
    cursor.executemany("""
        INSERT INTO readers (first_name, last_name, phone_number, password, role)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ("Fenny", "Lirst", "1234567890", "123", "Читатель"),
        ("Lenny", "First", "0987654321", "123", "Библиотекарь"),
        ("Hit", "Vandal", "88005353535", "123", "Читатель"),
        ("Van", "Darkholme", "0987643444", "123", "Читатель"),
        ("Billy", "Herrington", "88333333535", "123", "Читатель"),
    ])

    # Добавляем книги
    cursor.executemany("""
        INSERT INTO books (title, author, section)
        VALUES (?, ?, ?)
    """, [
        ("Программирование на Python", "Гвидо ван Россум", "Информатика"),
        ("Алгоритмы и структуры данных", "Никлаус Вирт", "Информатика"),
        ("Машинное обучение", "Андрю Нг", "Искусственный интеллект"),
        ("Сетевые технологии", "Тимоти Р. Фогель", "Телекоммуникации"),
        ("Теория баз данных", "Энтони Г. Мэр", "Информатика"),
        ("Кибербезопасность", "Ричард Снайдер", "Безопасность"),
        ("Искусственный интеллект: современный подход", "Стюарт Рассел", "Искусственный интеллект"),
        ("Программирование на C", "Брайан Керниган", "Программирование"),
        ("Совершенный код", "Стив Макконнелл", "Программирование"),
        ("Разработка программного обеспечения", "Роберт Л. Севил", "Информатика")
    ])

    # Добавляем экземпляры книг
    cursor.executemany("""
        INSERT INTO book_instances (book_id, storage_shelf, publisher, year, availability)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "A1", "O'Reilly", 2020, 1), 
        (2, "B2", "MIT Press", 2018, 1),
        (3, "A1", "O'Reilly", 2024, 1), 
        (4, "B2", "Питербург", 2018, 1),
        (5, "A1", "O'Reilly", 2020, 1), 
        (6, "B2", "MIT Press", 2018, 1),
        (7, "B2", "Питербург", 2018, 1),
        (8, "B2", "Питербург", 2018, 1),
        (9, "B2", "MIT Press", 2018, 1),
        (10, "A1", "O'Reilly", 2020, 1), 
        (2, "B2", "Vologda", 2018, 1),
        (1, "A1", "Питербург", 2020, 1), 
        (1, "B2", "Hoyoverse", 2018, 1),      
    ])

    # Добавляем журналы
    cursor.executemany("""
        INSERT INTO journals (title, issue, publication_date, section, availability, storage_shelf)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("Программирование и технологии", "Выпуск 1", "2023-01-01", "Программирование", 1, "A1"),
        ("Программирование и технологии", "Выпуск 2", "2023-02-01", "Программирование", 1, "A2"),
        ("Искусственный интеллект сегодня", "Выпуск 3", "2023-03-01", "Искусственный интеллект", 1, "B1"),
        ("Искусственный интеллект сегодня", "Выпуск 4", "2023-04-01", "Искусственный интеллект", 1, "B2"),
        ("Мир технологий", "Выпуск 5", "2023-05-01", "Технологии", 1, "C1"),
        ("Мир технологий", "Выпуск 6", "2023-06-01", "Технологии", 1, "C2"),
        ("Научный прогресс", "Выпуск 7", "2023-07-01", "Наука", 1, "D1"),
        ("Научный прогресс", "Выпуск 8", "2023-08-01", "Наука", 1, "D2"),
        ("Инновации в образовании", "Выпуск 9", "2023-09-01", "Образование", 1, "E1"),
        ("Инновации в образовании", "Выпуск 10", "2023-10-01", "Образование", 1, "E2"),
        ])

    # Добавляем выдачи
    cursor.executemany("""
        INSERT INTO loans (reader_id, book_instance_id, journal_id, issue_date, due_date, actual_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, 1, None, "2024-12-01", "2024-12-08", None), # Книга 1 выдана читателю 1
        (1, None, 1, "2024-12-01", "2024-12-15", None),
    ])

    # Добавляем очередь на журнал
    cursor.executemany("""
        INSERT INTO queues (reader_id, book_instance_id, journal_id, queue_position)
        VALUES (?, ?, ?, ?)
    """, [
        (3, None, 1, 1),  # Читатель 3 в очереди на журнал 1
        (4, None, 1, 2), 
    ])

    conn.commit()
    conn.close()

populate_test_data()
def fines():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO fines (reader_id, reason, amount, fine_date, loan_id)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "Просрочка сдачи", 300, "2024-12-14", 1),
    ])

    conn.commit()
    conn.close()

fines()

