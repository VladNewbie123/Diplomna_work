import flet as ft
import json
import os

# Шлях до файлу з даними користувача
USER_DATA_FILE = "user_data.json"


# Функція для завантаження даних з файлу
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {"personal_goals": []}


# Функція для збереження даних у файл
def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def personal_development_page(page, back_to_main):
    page.clean()

    # Завантаження цілей користувача з файлу
    user_data = load_user_data()
    personal_goals = user_data.get("personal_goals", [])

    # Колонка для відображення цілей
    goals_column = ft.Column(spacing=10)

    # Оновлення відображення списку цілей
    def update_goals_list():
        goals_column.controls.clear()
        for goal in personal_goals:
            goal_text = ft.Text(goal["text"], color="#FFFFFF", size=16, weight=ft.FontWeight.BOLD)
            if goal["completed"]:
                goal_text.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color="#00FF00")

            goals_column.controls.append(
                ft.Row(
                    [
                        goal_text,
                        ft.Checkbox(
                            value=goal["completed"],
                            on_change=lambda e, g=goal: toggle_goal_completed(g)
                        ),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, g=goal: delete_goal(g)),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                )
            )
        page.update()

    # Функція для додавання нової цілі
    def set_personal_goal(e):
        goal_input = ft.TextField(label="Введіть вашу ціль", width=300)

        def save_goal(event):
            goal_text = goal_input.value.strip()
            if goal_text:
                new_goal = {"text": goal_text, "completed": False}
                personal_goals.append(new_goal)
                user_data["personal_goals"] = personal_goals
                save_user_data(user_data)
                update_goals_list()
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Нова ціль", color="#FFD700"),
            content=goal_input,
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: close_dialog()),
                ft.TextButton("Зберегти", on_click=save_goal),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    # Закриття діалогу
    def close_dialog():
        page.dialog.open = False
        page.update()

    # Функція для видалення мети
    def delete_goal(goal):
        personal_goals.remove(goal)
        user_data["personal_goals"] = personal_goals
        save_user_data(user_data)
        update_goals_list()

    # Функція для позначення мети як виконаної/невиконаної
    def toggle_goal_completed(goal):
        goal["completed"] = not goal["completed"]
        save_user_data(user_data)
        update_goals_list()

    # Категорії розвитку
    development_options = ft.Column(
        [
            ft.ElevatedButton("Фізичний розвиток", on_click=lambda _: choose_physical_development()),
            ft.ElevatedButton("Інтелектуальний розвиток", on_click=lambda _: choose_intellectual_development()),
            ft.ElevatedButton("Емоційне здоров'я", on_click=lambda _: choose_emotional_health()),
            ft.ElevatedButton("Встановити ціль", on_click=set_personal_goal),
        ],
        spacing=10,
    )

    # Функції для вибору напрямку розвитку
    def choose_physical_development():
        page.clean()
        page.add(ft.Text("Фізичний розвиток", size=24, color="#FFD700"))
        page.add(ft.Text("Рекомендації: заняття спортом, правильне харчування, режим сну.", color="#FFFFFF"))
        page.add(ft.ElevatedButton("Назад", on_click=lambda _: personal_development_page(page, back_to_main)))

    def choose_intellectual_development():
        page.clean()
        page.add(ft.Text("Інтелектуальний розвиток", size=24, color="#FFD700"))
        page.add(ft.Text("Рекомендації: читання книг, онлайн-курси, вивчення мов.", color="#FFFFFF"))
        page.add(ft.ElevatedButton("Назад", on_click=lambda _: personal_development_page(page, back_to_main)))

    def choose_emotional_health():
        page.clean()
        page.add(ft.Text("Емоційне здоров'я", size=24, color="#FFD700"))
        page.add(ft.Text("Рекомендації: медитація, спілкування з близькими, психологічна підтримка.", color="#FFFFFF"))
        page.add(ft.ElevatedButton("Назад", on_click=lambda _: personal_development_page(page, back_to_main)))

    # Основний екран
    page.add(
        ft.Column(
            [
                ft.Text("Особистий розвиток", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                ft.Text("Тут можна вибрати напрямок для розвитку своїх особистих якостей.", color="#FFFFFF"),
                development_options,
                ft.Divider(color="#FFD700", thickness=1),
                ft.Text("Ваші персональні цілі:", size=20, color="#FFD700", weight=ft.FontWeight.BOLD),
                goals_column,
                ft.ElevatedButton("Повернутися", on_click=lambda _: back_to_main()),
            ],
            spacing=20,
            expand=True,
        )
    )

    update_goals_list()
