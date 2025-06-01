import flet as ft
import random
import functools
from db import get_categories_with_exercises, get_user_count, update_user_count
from pages.user_details_page import update_characteristics

# Отримуємо словник категорій з відповідними вправами з бази даних
categories = get_categories_with_exercises()

# Основна функція, яка створює сторінку зі спортивними завданнями
def sport_page(page: ft.Page, back_to_main, current_user_id):
    # Створюємо чекбокси для кожної категорії вправ
    category_checkboxes = [
        ft.Checkbox(
            label=category,
            value=False,
            label_style=ft.TextStyle(color="#C0C0C0"),
            on_change=lambda e, category=category: update_category_selection(category),
        )
        for category in categories.keys()
    ]

    # Колонка для відображення згенерованих завдань
    task_output = ft.Column()
    # Колонка для відображення виконаних завдань
    completed_tasks = ft.Column()

    # Функція повертає список вибраних категорій
    def selected_categories():
        return [cb.label for cb in category_checkboxes if cb.value]

    # Допоміжна функція — оновлює інформацію про вибрану категорію (для тестування/відладки)
    def update_category_selection(category):
        task_output.controls = [ft.Text(f"Вибрана категорія: {category}", color="#C0C0C0")]
        task_output.update()

    # Функція генерує до 3 завдань з випадкових вибраних категорій
    def generate_tasks(e):
        task_output.controls.clear()
        completed_tasks.controls.clear()
        completed_tasks.update()

        # Якщо не обрано жодної категорії — показати попередження
        if not selected_categories():
            task_output.controls.append(
                ft.Text("Будь ласка, виберіть хоча б одну категорію!", color="red")
            )
            task_output.update()
            return

        selected_exercises = set()
        available_exercises = []

        # Формуємо список доступних вправ із вибраних категорій
        for category in selected_categories():
            for exercise_name, default_count in categories[category]:
                # Отримуємо індивідуальну кількість повторень для вправи
                count = get_user_count(current_user_id, category, exercise_name) or default_count
                available_exercises.append((category, exercise_name, count))

        # Перемішуємо список вправ
        random.shuffle(available_exercises)

        # Додаємо до 3 унікальних вправ
        while len(selected_exercises) < 3 and available_exercises:
            chosen_category, task_name, count = available_exercises.pop()
            if task_name not in selected_exercises:
                selected_exercises.add(task_name)

                # Створюємо елемент зі вправою та кнопками для оцінки складності
                task_row = ft.Row([
                    ft.Text(f"{task_name} ({chosen_category}) – {count} разів", size=16, color="#D3D3D3"),
                    ft.ElevatedButton("Легко", on_click=functools.partial(rate_task, task_name, "Легко")),
                    ft.ElevatedButton("Нормально", on_click=functools.partial(rate_task, task_name, "Нормально")),
                    ft.ElevatedButton("Складно", on_click=functools.partial(rate_task, task_name, "Складно")),
                ])
                task_output.controls.append(task_row)

        task_output.update()
        # Оновлюємо характеристики користувача після генерації завдань
        update_characteristics(current_user_id)

    # Функція обробляє оцінку складності вправи користувачем
    def rate_task(task_name, rating, e):
        # Знаходимо категорію для цієї вправи
        category = next(
            (cat for cat, exercises in categories.items() if any(name == task_name for name, _ in exercises)),
            None
        )
        if not category:
            return

        # Отримуємо поточну кількість повторень для вправи
        current_count = get_user_count(current_user_id, category, task_name)
        if current_count is None:
            current_count = next((count for name, count in categories[category] if name == task_name), 5)

        # Змінюємо складність відповідно до оцінки
        if rating == "Складно":
            current_count = max(5, current_count - 5)  # Мінімум 5 повторень
        elif rating == "Легко":
            current_count += 5
        # Якщо "Нормально", не змінюємо count

        # Оновлюємо кількість у базі даних
        update_user_count(current_user_id, category, task_name, current_count)

        # Додаємо вправу до списку виконаних
        completed_tasks.controls.append(
            ft.Text(f"Виконано: {task_name} - {rating} ({current_count} разів)", color="green")
        )

        # Видаляємо вправу зі списку активних завдань
        for row in task_output.controls[:]:
            if any(task_name in str(c) for c in row.controls):
                task_output.controls.remove(row)

        task_output.update()
        completed_tasks.update()

    # Очищаємо сторінку та додаємо всі елементи
    page.clean()
    page.add(
        ft.Column([
            ft.Text("🏃‍♂️ Спорт", size=30, color="#FFA500", weight=ft.FontWeight.BOLD),  # Заголовок
            *[ft.Row(category_checkboxes[i:i + 3]) for i in range(0, len(category_checkboxes), 3)],  # Рядки з чекбоксами
            ft.ElevatedButton("Згенерувати завдання", on_click=generate_tasks),  # Кнопка генерації
            task_output,  # Виведення завдань
            ft.Text("✅ Виконані завдання:", size=18, color="#C0C0C0", weight=ft.FontWeight.BOLD),  # Заголовок для виконаних
            completed_tasks,  # Виведення виконаних
            ft.ElevatedButton("Повернутися", on_click=lambda _: back_to_main()),  # Кнопка повернення
        ], spacing=20)
    )
