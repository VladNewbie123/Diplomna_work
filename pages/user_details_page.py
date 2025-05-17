import flet as ft
import json


# Функція для перечитування user_data.json
def reload_user_data():
    with open("user_data.json", "r", encoding="utf-8") as file:
        return json.load(file)


# Функція для збереження змін до файлу
def save_user_data(user_data, file_path='user_data.json'):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(user_data, file, indent=4, ensure_ascii=False)


# Функція для оновлення характеристик та досвіду
def update_characteristics(user_data):
    # Визначення приросту характеристик для кожної категорії
    category_to_stat = {
        'Сила': 'strength',
        'Силова витривалість': 'endurance',
        'Швидкість': 'speed',
        'Гнучкість': 'endurance',
        'Розтяжка': 'endurance',
        'Кардіо': 'endurance',
        'Респіраторна система': 'endurance'
    }

    # Якщо попередніх даних немає, створюємо розділ "exercises_prev"
    if "exercises_prev" not in user_data:
        user_data["exercises_prev"] = {}

    # Якщо попередніх даних немає, створюємо розділ "education_prev"
    if "education_prev" not in user_data:
        user_data["education_prev"] = {}

    total_experience_gain = 0  # Загальний приріст досвіду для перевірки рівня

    # Обробка кожної категорії в exercises
    for category, exercises in user_data.get("exercises", {}).items():
        if category in category_to_stat:
            # Якщо в "exercises_prev" немає такої категорії, додаємо її
            if category not in user_data["exercises_prev"]:
                user_data["exercises_prev"][category] = {}

            for exercise, current_value in exercises.items():
                # Отримання попереднього значення
                prev_value = user_data["exercises_prev"][category].get(exercise, 0)

                # Обчислення різниці
                difference = current_value - prev_value

                # Якщо значення зросло, збільшуємо характеристику і досвід
                if difference > 0:
                    stat = category_to_stat[category]
                    user_data[stat] += difference
                    total_experience_gain += 10  # Приріст досвіду
                # Якщо значення зменшилося, зменшуємо характеристику і досвід
                elif difference < 0:
                    stat = category_to_stat[category]
                    user_data[stat] += difference  # Від'ємне значення зменшить характеристику
                    total_experience_gain += 5  # Від'ємне значення зменшить досвід

                # Оновлюємо значення в "exercises_prev"
                user_data["exercises_prev"][category][exercise] = current_value

    # Обробка кожної категорії в education
    for subject, topics in user_data.get("education", {}).items():
        if subject not in user_data["education_prev"]:
            user_data["education_prev"][subject] = {}

        for topic, current_data in topics.items():
            # Отримання попередніх даних
            prev_data = user_data["education_prev"][subject].get(topic, {})

            # Оцінка зміни рівня або статусу
            prev_is_learned = prev_data.get("is_learned", False)
            current_is_learned = current_data.get("is_learned", False)

            # Якщо статус змінився (наприклад, тема була усвоєна)
            if current_is_learned != prev_is_learned:
                if current_is_learned:
                    # Якщо тепер тема усвоєна, збільшуємо інтелект на 20
                    user_data["intelligence"] += 20
                    total_experience_gain += 10
                else:
                    # Якщо тепер тема не усвоєна, зменшуємо інтелект на 20
                    user_data["intelligence"] -= 20
                    total_experience_gain -= 10

            # Оновлюємо значення в "education_prev"
            user_data["education_prev"][subject][topic] = current_data

    # Оновлення досвіду після всіх змін
    user_data['experience'] += total_experience_gain

    # Перевірка на підвищення рівня
    if user_data['experience'] >= 100:
        user_data['level'] += 1
        user_data['experience'] = user_data['experience'] - 100  # Залишок досвіду після підвищення рівня

        # Підвищення всіх характеристик на 5 при підвищенні рівня
        user_data['strength'] += 5
        user_data['speed'] += 5
        user_data['endurance'] += 5
        user_data['intelligence'] += 5

    elif user_data['experience'] < 0:
        if user_data['level'] > 1:
            user_data['level'] -= 1
            user_data['experience'] = 90  # Залишаємо трохи досвіду після пониження
        else:
            user_data['experience'] = 0  # Не менше нуля на першому рівні

    # Збереження змін у файлі
    save_user_data(user_data)

    return user_data


def user_details_page(page, back_to_main, user_data):
    # Характеристики по центру в два стовпці
    def render_stats_section():
        updated_data = reload_user_data()
        stats_section = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(f"Сила: {updated_data['strength']}", size=16, color="#FFFFFF"),
                        ft.Text(f"Інтелект: {updated_data['intelligence']}", size=16, color="#FFFFFF"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Column(
                    [
                        ft.Text(f"Швидкість: {updated_data['speed']}", size=16, color="#FFFFFF"),
                        ft.Text(f"Витривалість: {updated_data['endurance']}", size=16, color="#FFFFFF"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        return stats_section

    # Оновлення рівня та досвіду
    def render_level_section():
        updated_data = reload_user_data()
        current_experience = updated_data["experience"]
        max_experience = 100  # Макс. досвід для підвищення рівня
        experience_progress = current_experience / max_experience

        return ft.Column(
            [
                ft.Text(f"🔰 Рівень: {updated_data['level']}", size=20, color="#FFD700", weight=ft.FontWeight.BOLD),
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

    # Оновлення характеристик після виконання вправ та збереження змін у файлі
    def update_stats(e):
        updated_data = reload_user_data()

        # Оновлюємо ім'я та вік з полів введення
        updated_data["name"] = name_input.value
        updated_data["age"] = age_input.value

        # Оновлюємо характеристики після вправ
        updated_data = update_characteristics(updated_data)

        # Зберігаємо оновлені дані у файл
        save_user_data(updated_data)

        # Оновлюємо контент сторінки для відображення змін
        update_page_content()

    # Функція для оновлення вмісту сторінки
    def update_page_content():
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Деталі користувача", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                    name_input,
                    age_input,
                    render_level_section(),  # Динамічна шкала досвіду
                    ft.Divider(color="#FFD700", thickness=1),
                    render_stats_section(),  # Динамічні характеристики
                    ft.Divider(color="#FFD700", thickness=1),
                    ft.ElevatedButton("Оновити", on_click=update_stats),  # Оновлення характеристик
                    ft.ElevatedButton("Повернутися", on_click=lambda _: back_to_main()),
                ],
                spacing=20,
                expand=True,
            )
        )

    # Початкове відображення сторінки
    update_page_content()
