import psycopg2
from psycopg2.extras import RealDictCursor

# Налаштування підключення до БД
db_config = {
    "host": "localhost",
    "port": "5432",
    "database": "diploma_app",
    "user": "postgres",
    "password": "turtur"
}


# Функція для створення нового підключення до БД
def get_connection():
    return psycopg2.connect(**db_config)


# Тимчасова функція для хешування пароля (поки що просто повертає пароль без змін)
def hash_password(password): return password  # тимчасово


# Функція перевірки пароля (порівнює простий текст пароля)
def verify_password(raw_password, stored_password): return raw_password == stored_password


# Функція створення нового користувача в базі даних
def create_user(username, raw_password, role_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hash_password(raw_password)  # хешуємо пароль
        cursor.execute("""
            INSERT INTO users (name, password_hash, role_id)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (username, hashed, role_id))
        user_id = cursor.fetchone()[0]  # отримуємо ID створеного користувача
        conn.commit()
        return user_id
    finally:
        cursor.close()
        conn.close()


# Функція отримання користувача за ім'ям (username)
def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT users.id, users.name, users.password_hash, roles.name as role_name
            FROM users
            JOIN roles ON users.role_id = roles.id
            WHERE users.name = %s;
        """, (username,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "password_hash": row[2],
                "role": row[3]
            }
        return None
    finally:
        cursor.close()
        conn.close()


# --- Функції роботи з даними користувача ---
# Завантажуємо дані користувача за його ID
def load_user_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, age, strength, intelligence, speed, endurance, balance, level, experience
            FROM users
            WHERE id = %s;
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": user_id,  # ID користувача
                "name": row[1],
                "age": row[2],
                "strength": row[3],
                "intelligence": row[4],
                "speed": row[5],
                "endurance": row[6],
                "balance": row[7],
                "level": row[8],
                "experience": row[9]
            }
        return None
    finally:
        cursor.close()
        conn.close()


# Збереження оновлених даних користувача в базу
def save_user_data(user_id, user_data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users SET
                name = %s,
                age = %s,
                strength = %s,
                intelligence = %s,
                speed = %s,
                endurance = %s,
                balance = %s,
                level = %s,
                experience = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (
            user_data["name"],
            user_data["age"],
            int(user_data["strength"]),
            int(user_data["intelligence"]),
            int(user_data["speed"]),
            int(user_data["endurance"]),
            int(user_data["balance"]),
            int(user_data["level"]),
            int(user_data["experience"]),
            user_id
        ))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# --- Функції, пов'язані з ролями користувачів ---
# Отримати роль користувача за його ID
def get_user_role(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT roles.name
            FROM users
            JOIN roles ON users.role_id = roles.id
            WHERE users.id = %s;
        """, (user_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        conn.close()

# Ініціалізація таблиці прогресу користувача, якщо її ще немає
def initialize_user_progress_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            category TEXT,
            exercise TEXT,
            count INTEGER,
            PRIMARY KEY (category, exercise)
        )
    """)
    conn.commit()
    conn.close()

# Оновлення прогресу користувача (кількість виконань вправи)
def update_user_progress(user_id, category, exercise, count):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_progress (user_id, category, exercise, count)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, category, exercise)
        DO UPDATE SET count = EXCLUDED.count
    """, (user_id, category, exercise, count))
    conn.commit()
    conn.close()

# Отримати прогрес користувача за категорією та вправою
def get_user_progress(user_id, category, exercise_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT count, last_count FROM user_progress
        WHERE user_id = %s AND category = %s AND exercise_name = %s
    """, (user_id, category, exercise_name))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, 0)

# Оновити кількість виконань вправи користувачем
def update_user_count(user_id, category, exercise_name, count):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_progress (user_id, category, exercise_name, count, updated_at)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id, category, exercise_name)
        DO UPDATE SET count = EXCLUDED.count, updated_at = CURRENT_TIMESTAMP
    """, (user_id, category, exercise_name, count))
    conn.commit()
    cur.close()
    conn.close()

# Отримати кількість виконань вправи користувачем
def get_user_count(user_id, category, exercise_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT count FROM user_progress
        WHERE user_id = %s AND category = %s AND exercise_name = %s
    """, (user_id, category, exercise_name))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

# Отримати всі категорії вправ з їхніми вправами (список)
def get_categories_with_exercises():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT ec.name AS category_name, et.name AS exercise_name
        FROM exercise_categories ec
        LEFT JOIN exercise_templates et ON et.category_id = ec.id
        ORDER BY ec.name
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    categories = {}
    for category_name, exercise_name in rows:
        if category_name not in categories:
            categories[category_name] = []
        if exercise_name:
            categories[category_name].append((exercise_name, 5))  # 5 - кількість за замовчуванням
    return categories

# Отримати відповідність категорій вправ до статів користувача
def get_category_to_stat_map():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, related_stat FROM exercise_categories")
    rows = cursor.fetchall()
    conn.close()
    return {name: stat for name, stat in rows}

# Збереження результату тестування користувача
def save_quiz_result(user_id, quiz_id, score, passed):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_results (user_id, quiz_id, score, passed)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, quiz_id)
        DO UPDATE SET score = EXCLUDED.score, passed = EXCLUDED.passed
    """, (user_id, quiz_id, score, passed))
    conn.commit()
    cursor.close()
    conn.close()


# --- Функції для роботи з предметами, темами, матеріалами та тестами ---
# 1. Отримати всі предмети
def get_all_subjects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    return cursor.fetchall()


# 2. Отримати теми за subject_id
def get_topics_by_subject(subject_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics WHERE subject_id = %s", (subject_id,))
    return cursor.fetchall()


# 3. Отримати матеріали за topic_id
def get_materials_by_topic(topic_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials WHERE topic_id = %s", (topic_id,))
    return cursor.fetchall()


# 4. Отримати тест за topic_id
def get_quiz_by_topic(topic_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE topic_id = %s", (topic_id,))
    return cursor.fetchone()


# 5. Отримати питання і відповіді для тесту
def get_questions_and_answers(quiz_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Отримати питання з урахуванням рівня складності
    cursor.execute("""
        SELECT id, text, difficulty_level
        FROM questions
        WHERE quiz_id = %s
        ORDER BY difficulty_level
    """, (quiz_id,))
    questions = cursor.fetchall()
    result = []
    for question in questions:
        question_id, question_text, difficulty_level = question
        # Отримати відповіді для кожного питання
        cursor.execute("""
            SELECT id, text, is_correct
            FROM answers
            WHERE question_id = %s
        """, (question_id,))
        answers = cursor.fetchall()
        result.append({
            "question_id": question_id,
            "question_text": question_text,
            "difficulty_level": difficulty_level,
            "answers": [
                {"answer_id": a[0], "text": a[1], "is_correct": a[2]} for a in answers
            ]
        })
    return result


# 6. Зберегти результат тесту
def saves_quiz_result(user_id, quiz_id, score, passed):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_results (user_id, quiz_id, score, passed)
        VALUES (%s, %s, %s, %s)
    """, (user_id, quiz_id, score, passed))
    conn.commit()


# 7. Отримати прогрес користувача
def get_user_education(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_education_progress WHERE user_id = %s", (user_id,))
    return cursor.fetchall()


# 8. Оновити або додати запис у таблицю education
def update_education_status(user_id, topic_id, test_passed=False, materials_unlocked=False, quiz_block=0):
    conn = get_connection()
    cursor = conn.cursor()
    # Перевірка, чи існує запис
    cursor.execute("""
        SELECT * FROM user_education_progress
        WHERE user_id = %s AND topic_id = %s AND quiz_block = %s
    """, (user_id, topic_id, quiz_block))
    existing = cursor.fetchone()
    if existing:
        # Оновити наявний запис (не чіпаємо progress_counted!)
        cursor.execute("""
            UPDATE user_education_progress
            SET test_passed = %s, materials_unlocked = %s
            WHERE user_id = %s AND topic_id = %s
        """, (test_passed, materials_unlocked, existing[0]))
    else:
        # Додати новий запис — і тут progress_counted автоматично = FALSE за замовчуванням
        cursor.execute("""
            INSERT INTO user_education_progress (user_id, topic_id, test_passed, materials_unlocked, quiz_block)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, topic_id, test_passed, materials_unlocked, quiz_block))
    conn.commit()
    conn.close()


def load_personal_goals(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, goal, is_completed FROM personal_goals WHERE user_id = %s ORDER BY id;", (user_id,))
            return cur.fetchall()


def add_personal_goal(user_id, goal_text):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO personal_goals (user_id, goal) VALUES (%s, %s);",
                (user_id, goal_text)
            )
            conn.commit()


def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return cursor.rowcount > 0  # True якщо користувача видалено
    finally:
        cursor.close()
        conn.close()


def is_admin(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role_id FROM users WHERE id = %s;", (user_id,))
        row = cursor.fetchone()
        if row:
            return row[0] == 2  # 2 — це адміністратор
        return False
    finally:
        cursor.close()
        conn.close()


def load_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, age, strength, intelligence, speed, endurance, balance, level, experience, role_id
            FROM users
            WHERE role_id = 1;
        """)
        rows = cursor.fetchall()
        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "name": row[1],
                "age": row[2],
                "strength": row[3],
                "intelligence": row[4],
                "speed": row[5],
                "endurance": row[6],
                "balance": row[7],
                "level": row[8],
                "experience": row[9],
                "role_id": row[10]
            })
        return users
    finally:
        cursor.close()
        conn.close()
