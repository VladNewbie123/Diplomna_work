import flet as ft
from db import load_user_data, save_user_data, get_user_progress, get_user_education, get_categories_with_exercises, \
    get_connection, get_category_to_stat_map


# 🧠 Функція для оновлення характеристик та досвіду користувача на основі виконаних вправ та освітнього прогресу
def update_characteristics(user_id):
    user_data = load_user_data(user_id)

    # Початкові значення змін характеристик
    total_strength = 0
    total_speed = 0
    total_endurance = 0
    total_balance = 0
    total_intelligence = 0

    # Збереження попередніх значень характеристик
    old_strength = user_data["strength"]
    old_speed = user_data["speed"]
    old_endurance = user_data["endurance"]
    old_balance = user_data["balance"]
    old_intelligence = user_data["intelligence"]

    # Отримуємо категорії вправ та карту відповідності категорій характеристикам
    categories = get_categories_with_exercises()
    category_to_progress_type = get_category_to_stat_map()

    conn = get_connection()
    cursor = conn.cursor()

    # 🔁 Перебираємо категорії та вправи, щоб розрахувати прогрес
    for category, exercises in categories.items():
        for exercise_name, base_count in exercises:
            user_count, last_count = get_user_progress(user_id, category, exercise_name)

            delta = user_count - last_count
            if delta > 0:
                progress_type = category_to_progress_type.get(category)

                # Додаємо приріст до відповідної характеристики
                if progress_type == "strength":
                    total_strength += delta
                elif progress_type == "speed":
                    total_speed += delta
                elif progress_type == "endurance":
                    total_endurance += delta
                elif progress_type == "intelligence":
                    total_intelligence += delta
                elif progress_type == "balance":
                    total_balance += delta

                # Оновлюємо last_count у базі даних
                cursor.execute("""
                        UPDATE user_progress
                        SET last_count = %s
                        WHERE user_id = %s AND category = %s AND exercise_name = %s
                    """, (user_count, user_id, category, exercise_name))

    # 🧠 Додаткове оновлення інтелекту за завершені освітні блоки, які ще не були враховані
    cursor.execute("""
           SELECT id, quiz_block
           FROM user_education_progress
           WHERE user_id = %s AND test_passed = TRUE AND progress_counted = FALSE
       """, (user_id,))
    new_intelligence_rows = cursor.fetchall()

    for row_id, quiz_block in new_intelligence_rows:
        if quiz_block == 0:
            total_intelligence += 5
        elif quiz_block == 1:
            total_intelligence += 8
        elif quiz_block == 2:
            total_intelligence += 10

        # Позначаємо, що цей блок вже врахований
        cursor.execute("""
               UPDATE user_education_progress
               SET progress_counted = TRUE
               WHERE id = %s
           """, (row_id,))

    # ✅ Оновлюємо характеристики користувача з урахуванням обмеження максимуму 100
    user_data["strength"] = min(user_data["strength"] + total_strength * 0.2, 100)
    user_data["speed"] = min(user_data["speed"] + total_speed * 0.2, 100)
    user_data["endurance"] = min(user_data["endurance"] + total_endurance * 0.2, 100)
    user_data["balance"] = min(user_data["balance"] + total_endurance * 0.2, 100)
    user_data["intelligence"] = min(user_data["intelligence"] + total_intelligence * 0.2, 100)

    # 🔄 Перевірка змін характеристик
    characteristics_increased = (
            user_data["strength"] > old_strength or
            user_data["speed"] > old_speed or
            user_data["endurance"] > old_endurance or
            user_data["balance"] > old_balance or
            user_data["intelligence"] > old_intelligence
    )

    characteristics_decreased = (
            user_data["strength"] < old_strength or
            user_data["speed"] < old_speed or
            user_data["endurance"] < old_endurance or
            user_data["balance"] < old_balance or
            user_data["intelligence"] < old_intelligence
    )

    # ⭐ Оновлюємо досвід в залежності від змін
    if characteristics_increased:
        user_data["experience"] = min(user_data["experience"] + 10, 200)
    elif characteristics_decreased:
        user_data["experience"] = max(user_data["experience"] - 10, 0)

    # ⬆️ Підвищення рівня при досягненні 100 досвіду
    while user_data["experience"] >= 100:
        user_data["experience"] -= 100
        user_data["level"] += 1

    conn.commit()
    conn.close()

    # 💾 Збереження оновлених даних користувача
    save_user_data(user_id, user_data)


# 📄 Сторінка з деталями користувача
def user_details_page(page, back_to_main, user_data):
    # 📊 Відображення характеристик користувача у вигляді трьох колонок
    def render_stats_section():
        stats_section = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(f"Сила: {user_data['strength']}", size=16, color="#FFFFFF"),
                        ft.Text(f"Координація: {user_data['balance']}", size=16, color="#FFFFFF"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Column(
                    [
                        ft.Text(f"Інтелект: {user_data['intelligence']}", size=16, color="#FFFFFF")
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Column(
                    [
                        ft.Text(f"Швидкість: {user_data['speed']}", size=16, color="#FFFFFF"),
                        ft.Text(f"Витривалість: {user_data['endurance']}", size=16, color="#FFFFFF"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        return stats_section

    # 🎮 Відображення рівня та досвіду користувача
    def render_level_section():
        current_experience = user_data["experience"]
        max_experience = 100
        experience_progress = current_experience / max_experience

        return ft.Column(
            [
                ft.Text(f"🔰 Рівень: {user_data['level']}", size=20, color="#FFD700", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.ProgressBar(value=experience_progress, color="#FFD700"),
                    height=20,
                    border_radius=5,
                    bgcolor="#3E3E56",
                    expand=True,
                ),
                ft.Container(
                    content=ft.Text(
                        f"{current_experience}/{max_experience}",
                        size=14,
                        color="#FFFFFF",
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    alignment=ft.alignment.bottom_right,
                    padding=ft.Padding(0, 2, 0, 0),
                    expand=True,
                ),
            ],
            spacing=10,
        )

    # 📥 Поля для редагування імені та віку
    name_input = ft.TextField(
        label="Ім'я",
        label_style=ft.TextStyle(color="#B0B0B0"),
        value=user_data["name"],
        color="#FFFFFF",
        border_color="#FFD700"
    )
    age_input = ft.TextField(
        label="Вік",
        label_style=ft.TextStyle(color="#B0B0B0"),
        value=user_data["age"],
        color="#FFFFFF",
        border_color="#FFD700"
    )

    # 🔙 Обробка кнопки повернення — зберігаємо зміни та переходимо назад
    def on_back():
        user_data["name"] = name_input.value
        user_data["age"] = age_input.value
        save_user_data(user_data["id"], user_data)
        back_to_main()

    # 🔄 Оновлення сторінки з актуальними даними користувача
    def update_page_content():
        updated_data = load_user_data(user_data["id"])
        user_data.update(updated_data)  # синхронізація

        update_characteristics(user_data["id"])  # оновлення характеристик

        updated_data = load_user_data(user_data["id"])
        user_data.update(updated_data)

        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Деталі користувача", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                    name_input,
                    age_input,
                    render_level_section(),
                    ft.Divider(color="#FFD700", thickness=1),
                    render_stats_section(),
                    ft.Divider(color="#FFD700", thickness=1),
                    ft.ElevatedButton("Повернутися", on_click=lambda _: on_back()),
                ],
                spacing=20,
                expand=True,
            )
        )

    # 📌 Ініціалізація сторінки
    update_page_content()
