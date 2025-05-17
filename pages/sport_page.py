import flet as ft
import json
import random
import functools
import os

# 🔹 Перемістимо categories у глобальну область видимості
categories = {
    "Розтяжка": [
        ("Розтяжка для спини хвилин", 15),
        ("Розтяжка ніг хвилин", 15),
        ("Йога хвилин", 20),
        ("Розтяжка рук хвилин", 15),
        ("Розтяжка шиї хвилин", 10),
        ("Силова розтяжка хвилин", 20)
    ],
    "Сила": [
        ("Присідання", 10),
        ("Прес", 15),
        ("Віджимання", 10),
        ("Підтягування", 5),
        ("Мертва тяга", 10),
        ("Жим лежачи", 10)
    ],
    "Кардіо": [
        ("Біг хвилин", 30),
        ("Стрибки на місці", 20),
        ("Скакалка", 30),
        ("Велотренажер хвилин", 10),
        ("Еліптичний тренажер хвилин", 10),
        ("Плавання хвилин", 10)
    ],
    "Гнучкість": [
        ("Пілатес хвилин", 20),
        ("Йога для початківців хвилин", 20),
        ("Акробатика хвилин", 25),
        ("Балет хвилин", 30),
        ("Стретчинг", 20),
        ("Гімнастика хвилин", 25)
    ],
    "Силова витривалість": [
        ("Планка хвилин", 30),
        ("Турнік", 10),
        ("Бурпі хвилин", 10),
        ("Присідання з гирею", 10),
        ("Кроссфіт", 20),
        ("Тренування з гирями", 15)
    ],
    "Респіраторна система": [
        ("Дихальні вправи хвилин", 5),  # хвилин
        ("Біг на великі дистанції хвилин", 10),
        ("Вправи для легень хвилин", 5),
        ("Йога дихання хвилин", 5),
        ("Тренування на витривалість хвилин", 30)
    ],
    "Швидкість": [
        ("Спринт на метрів", 100),
        ("Біг по сходах", 5),
        ("Швидкі стрибки хвилин", 10),
        ("Тренування на швидкість хвилин", 20),
        ("Тренування на реакцію хвилин", 15)
    ],
    "Робота з вагою тіла": [
        ("Присідання", 10),
        ("Віджимання", 10),
        ("Підтягування", 5),
        ("Випади", 10),
        ("Планка", 30),
        ("Тренування на всі групи м'язів хвилин", 20)
    ],
    "Аеробні навантаження": [
        ("Велосипед хвилин", 40),
        ("Біг на довгі дистанції", 60),
        ("Плавання хвилин", 50),
        ("Стрибки на скакалці", 30),
        ("Танці хвилин", 45),
        ("Кардіотренажери", 50)
    ],
    "Функціональне тренування": [
        ("TRX", 20),
        ("Кроссфіт", 25),
        ("Функціональні рухи", 30),
        ("Гімнастичні вправи", 20),
        ("Комплекс вправ", 30)
    ],
    "Баланс та координація": [
        ("Баланс на одній нозі", 15),
        ("Гімнастичний м'яч", 20),
        ("Йога на баланс", 25),
        ("Скакалка", 30),
        ("Лестничні вправи", 20)
    ],
    "Релаксація": [
        ("Медитація хвилин", 10),  # хвилин
        ("Дихальні практики", 10),
        ("Йога для розслаблення хвилин", 15),
        ("Прогулянка на природі хвилин", 30),
        ("Роллінг", 20)
    ]
}


# 🔹 Функція ініціалізації user_data.json значеннями з categories
def initialize_user_data():
    if not os.path.exists("user_data.json"):
        user_data = {"exercises": {}}
        for category, exercises in categories.items():
            user_data["exercises"][category] = {}  # Додаємо категорію як ключ
            for exercise, default_count in exercises:
                user_data["exercises"][category][exercise] = default_count  # Вкладаємо вправу в категорію

        with open("user_data.json", "w", encoding="utf-8") as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)


# Викликаємо ініціалізацію, щоб user_data.json створився до роботи з ним
initialize_user_data()


# 🔹 Функція для оновлення значень у user_data.json
def update_user_data(task, new_count):
    try:
        with open("user_data.json", "r", encoding="utf-8") as file:
            user_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {"exercises": {}}

    # Пошук категорії для вправи
    for category, exercises in categories.items():
        if task in [exercise[0] for exercise in exercises]:
            if category not in user_data["exercises"]:
                user_data["exercises"][category] = {}  # Якщо категорії немає, створюємо
            user_data["exercises"][category][task] = new_count  # Оновлюємо значення
            break

    with open("user_data.json", "w", encoding="utf-8") as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)


# 🔹 Основна функція сторінки спорту
def sport_page(page, back_to_main):
    category_checkboxes = [
        ft.Checkbox(
            label=category,
            value=False,
            label_style=ft.TextStyle(color="#C0C0C0"),  # Світліший текст
            on_change=lambda e, category=category: update_category_selection(e, category),
        )
        for category in categories.keys()
    ]

    task_output = ft.Column()
    completed_tasks = ft.Column()

    def selected_categories():
        return [checkbox.label for checkbox in category_checkboxes if checkbox.value]

    def update_category_selection(category):
        task_output.controls = [ft.Text(f"Вибрана категорія: {category}", color="#C0C0C0")]
        task_output.update()

    def generate_tasks(e):
        task_output.controls.clear()
        completed_tasks.controls.clear()
        completed_tasks.update()

        if not selected_categories():
            task_output.controls.append(ft.Text("Будь ласка, виберіть хоча б одну категорію!", color="red"))
        else:
            selected_exercises = set()  # Множина для унікальних завдань
            available_exercises = []

            # Збираємо всі можливі вправи з обраних категорій
            for category in selected_categories():
                available_exercises.extend([(category, exercise, count) for exercise, count in categories[category]])

            # Перемішуємо список можливих завдань
            random.shuffle(available_exercises)

            # Вибираємо максимум 3 унікальні вправи
            while len(selected_exercises) < 3 and available_exercises:
                chosen_category, task_name, default_count = available_exercises.pop()

                if task_name not in selected_exercises:  # Перевірка унікальності
                    selected_exercises.add(task_name)

                    try:
                        with open("user_data.json", "r", encoding="utf-8") as file:
                            user_data = json.load(file)
                    except (FileNotFoundError, json.JSONDecodeError):
                        user_data = {"exercises": {}}

                    count = user_data["exercises"].get(chosen_category, {}).get(task_name, default_count)

                    task_row = ft.Row([
                        ft.Text(f"{task_name} ({chosen_category}) – {count}", size=16, color="#D3D3D3"),
                        ft.ElevatedButton("Легко", on_click=functools.partial(rate_task, task_name, "Легко")),
                        ft.ElevatedButton("Нормально", on_click=functools.partial(rate_task, task_name, "Нормально")),
                        ft.ElevatedButton("Складно", on_click=functools.partial(rate_task, task_name, "Складно")),
                    ])
                    task_output.controls.append(task_row)

        task_output.update()

    def rate_task(task, rating, e):
        try:
            with open("user_data.json", "r", encoding="utf-8") as file:
                user_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_data = {"exercises": {}}

        # Отримуємо стандартне значення з categories, якщо його немає в user_data.json
        default_count = next(
            (count for exercises in categories.values() for name, count in exercises if name == task), 5
        )
        current_count = user_data["exercises"].get(task, default_count)

        if rating == "Складно":
            current_count = max(5, current_count - 5)  # Мінімум 5
        elif rating == "Легко":
            current_count += 5

        update_user_data(task, current_count)

        completed_tasks.controls.append(ft.Text(f"Виконано: {task} - {rating} ({current_count} разів)", color="green"))
        # Видаляємо виконане завдання з активного списку
        for row in task_output.controls[:]:  # Робимо копію списку, щоб уникнути помилок при зміні
            if any(task in str(c) for c in row.controls):  # Перевіряємо, чи є назва завдання в елементах
                task_output.controls.remove(row)
        task_output.update()
        completed_tasks.update()

    page.clean()
    page.add(
        ft.Column([
            ft.Text("🏃‍♂️ Спорт", size=30, color="#FFA500", weight=ft.FontWeight.BOLD),
            *[ft.Row(category_checkboxes[i:i + 3]) for i in range(0, len(category_checkboxes), 3)],
            ft.ElevatedButton("Згенерувати завдання", on_click=generate_tasks),
            task_output,
            ft.Text("✅ Виконані завдання:", size=18, color="#C0C0C0", weight=ft.FontWeight.BOLD),
            completed_tasks,
            ft.ElevatedButton("Повернутися", on_click=lambda _: back_to_main()),
        ], spacing=20)
    )
