import flet as ft
from db import load_user_data  # Імпортуємо функцію з db.py


# Функція для створення заголовка
def create_header():
    return ft.Container(
        content=ft.Text(
            "Асистент: Підвищення рівня ️",  # Текст заголовка
            size=30,  # Розмір шрифту
            color="#FFD700",  # Колір шрифту
            weight=ft.FontWeight.BOLD,  # Жирний шрифт
            text_align=ft.TextAlign.CENTER,  # Вирівнювання тексту по центру
        ),
        padding=20,  # Відступи всередині контейнера
        alignment=ft.alignment.center,  # Вирівнювання контейнера
    )


# Функція для створення статусу користувача
def create_user_status(user_id, navigate_to_user_details):
    updated_data = load_user_data(user_id)  # Завантажуємо дані користувача
    if not updated_data:
        updated_data = {
            "level": 1,
            "experience": 0
        }
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(f"🔰 Рівень: {updated_data['level']}", size=18, color="#FFD700", weight=ft.FontWeight.BOLD),
                ft.Text(f"🧪 Досвід: {updated_data['experience']}/100", size=18, color="#FFFFFF"),
                ft.ElevatedButton("Деталі користувача", on_click=lambda _: navigate_to_user_details()),
                # Кнопка для переходу до деталей користувача
            ],
            spacing=10,  # Простір між елементами
        ),
        padding=20,  # Відступи всередині контейнера
        margin=10,  # Зовнішні відступи
        bgcolor="#4A4A6A",  # Колір фону контейнера
        border_radius=15,  # Радіус скруглення контейнера
    )


# Функція для створення панелі логів
def create_log_panel():
    return ft.Container(
        content=ft.Column([], spacing=5),  # Панель для виведення логів
        padding=20,  # Відступи всередині контейнера
        margin=10,  # Зовнішні відступи
        bgcolor="#2E2E3E",  # Колір фону контейнера
        border_radius=15,  # Радіус скруглення
        expand=True,  # Розширення контейнера на весь доступний простір
    )


# Функція для створення поля вводу команд користувача
def create_user_input(on_submit):
    return ft.TextField(
        label="Введіть команду...('допомога')",  # Підказка для користувача
        label_style=ft.TextStyle(color="#B0B0B0"),  # Стиль підказки
        border_color="#FFD700",  # Колір межі
        color="#FFFFFF",  # Колір тексту
        cursor_color="#FFD700",  # Колір курсора
        on_submit=lambda e: on_submit(e.control.value),  # Обробник події при натисканні Enter
    )
