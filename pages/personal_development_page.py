# Імпортуємо необхідні бібліотеки
from datetime import datetime
import flet as ft
from db import get_connection, load_personal_goals, add_personal_goal, load_user_data
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import io
import base64

# Кеш для збереження зображень радарних діаграм (щоб не будувати повторно)
radar_cache = {}


# Функція для створення радарної діаграми на основі характеристик користувача
def create_radar_chart(user_data: dict, norm: int = 80) -> str:
    matplotlib.use('Agg')  # Встановлюємо бекенд без GUI
    user_key = str(user_data)

    # Якщо зображення вже є в кеші — повертаємо його
    if user_key in radar_cache:
        return radar_cache[user_key]

    # Мітки для діаграми
    labels = ["Сила", "Швидкість", "Витривалість", "Баланс", "Інтелект"]
    values = [
        user_data["strength"],
        user_data["speed"],
        user_data["endurance"],
        user_data["balance"],
        user_data["intelligence"],
    ]
    norms = [norm] * len(values)

    # Розрахунок кутів для побудови діаграми
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]  # Замикання кола
    norms += norms[:1]
    angles += angles[:1]

    # Створення фігури та осі
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, norms, label="Норма", color="gray", linestyle="--")
    ax.plot(angles, values, label="Користувач", color="gold")
    ax.fill(angles, values, color="gold", alpha=0.4)

    # Налаштування зовнішнього вигляду діаграми
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    ax.set_title("Характеристики")
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))

    # Збереження діаграми у форматі base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=150)
    buffer.seek(0)
    plt.close(fig)

    # Звільнення памʼяті
    del fig, ax

    # Кодуємо зображення та зберігаємо у кеш
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    radar_cache[user_key] = image_base64
    return image_base64


# Основна функція для сторінки особистого розвитку
def personal_development_page(page, back_to_main, user_id):
    page.clean()  # Очищення сторінки

    # Колонка для виведення списку цілей користувача
    goals_column = ft.Column(spacing=10)

    # Функція для оновлення списку цілей
    def update_goals_list():
        goals_column.controls.clear()
        goals = load_personal_goals(user_id)

        for goal in goals:
            goal_text = ft.Text(goal["goal"], color="#FFFFFF", size=16, weight=ft.FontWeight.BOLD)
            if goal["is_completed"]:
                goal_text.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color="#00FF00")

            goals_column.controls.append(
                ft.Row(
                    [
                        goal_text,
                        # Чекбокс для позначення завершення цілі
                        ft.Checkbox(
                            value=goal["is_completed"],
                            on_change=lambda e, gid=goal["id"], status=not goal["is_completed"]: toggle_goal_completed(
                                gid, status) or update_goals_list()
                        ),
                        # Кнопка для видалення цілі
                        ft.IconButton(ft.icons.DELETE,
                                      on_click=lambda e, gid=goal["id"]: delete_goal(gid) or update_goals_list()),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                )
            )
        page.update()

    # Функція для створення нової цілі
    def set_personal_goal(e):
        goal_input = ft.TextField(label="Введіть вашу ціль", width=300)

        def save_goal(event):
            goal_text = goal_input.value.strip()
            if goal_text:
                add_personal_goal(user_id, goal_text)
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

    # Функція для закриття діалогового вікна
    def close_dialog():
        page.dialog.open = False
        page.update()

    # Функція для видалення цілі
    def delete_goal(goal_id):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM personal_goals WHERE id = %s;", (goal_id,))
                conn.commit()

    # Функція для оновлення статусу цілі (виконано/не виконано)
    def toggle_goal_completed(goal_id, new_status):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE personal_goals SET is_completed = %s, updated_at = %s WHERE id = %s;",
                    (new_status, datetime.now(), goal_id)
                )
                conn.commit()

    # Блок з кнопками вибору напрямків розвитку
    development_options = ft.Column(
        [
            ft.ElevatedButton("Фізичний розвиток", on_click=lambda _: choose_physical_development()),
            ft.ElevatedButton("Інтелектуальний розвиток", on_click=lambda _: choose_intellectual_development()),
            ft.ElevatedButton("Емоційне здоров'я", on_click=lambda _: choose_emotional_health()),
            ft.ElevatedButton("Встановити ціль", on_click=set_personal_goal),
        ],
        spacing=10,
    )

    # Функції для переходу до різних напрямків розвитку
    def choose_physical_development():
        page.clean()
        page.add(ft.Text("Фізичний розвиток", size=24, color="#FFD700"))
        page.add(ft.Text("Рекомендації: заняття спортом, правильне харчування, режим сну.", color="#FFFFFF"))
        page.add(ft.ElevatedButton("Назад", on_click=lambda _: personal_development_page(page, back_to_main, user_id)))

    def choose_intellectual_development():
        page.clean()
        page.add(ft.Text("Інтелектуальний розвиток", size=24, color="#FFD700"))
        page.add(ft.Text("Рекомендації: читання книг, онлайн-курси, вивчення мов.", color="#FFFFFF"))
        page.add(ft.ElevatedButton("Назад", on_click=lambda _: personal_development_page(page, back_to_main, user_id)))

    def choose_emotional_health():
        page.clean()
        page.add(ft.Text("Емоційне здоров'я", size=24, color="#FFD700"))
        page.add(ft.Text("Рекомендації: медитація, спілкування з близькими, психологічна підтримка.", color="#FFFFFF"))
        page.add(ft.ElevatedButton("Назад", on_click=lambda _: personal_development_page(page, back_to_main, user_id)))

    # Завантаження характеристик користувача та створення радарної діаграми
    user_data = load_user_data(user_id)
    radar_base64 = create_radar_chart(user_data)
    radar_image = ft.Image(src_base64=radar_base64, width=350, height=350)

    # Головний блок із діаграмою та кнопками розвитку
    blog = ft.Row([development_options,
                   ft.Text("Ваші характеристики:", size=20, color="#FFD700", weight=ft.FontWeight.BOLD),
                   radar_image
                   ], spacing=50)

    # Основна структура сторінки
    page.add(
        ft.Column(
            [
                ft.Text("Особистий розвиток", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                ft.Text("Тут можна вибрати напрямок для розвитку своїх особистих якостей.", color="#FFFFFF"),
                blog,
                ft.Divider(color="#FFD700", thickness=1),
                ft.Text("Ваші персональні цілі:", size=20, color="#FFD700", weight=ft.FontWeight.BOLD),
                goals_column,
                ft.ElevatedButton("Повернутися", on_click=lambda _: back_to_main()),
            ],
            spacing=20,
            expand=True,
        )
    )

    # Перший виклик для відображення цілей
    update_goals_list()
