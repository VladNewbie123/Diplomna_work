import flet as ft
import json
from pages.user_details_page import user_details_page
from pages.personal_development_page import personal_development_page
from pages.education_page import education_page
from pages.sport_page import sport_page
from ui_components import create_header, create_user_status, create_log_panel, create_user_input
from logic import process_command


# Функція для завантаження даних користувача з файлу JSON
def load_user_data():
    try:
        with open("user_data.json", "r", encoding="utf-8") as file:
            return json.load(file)  # Повертає дані користувача у вигляді словника
    except FileNotFoundError:
        # Якщо файл не знайдено, створюється шаблон даних користувача
        return {
            "name": "Користувач",
            "age": "",
            "strength": 0,
            "intelligence": 0,
            "speed": 0,
            "endurance": 0,
            "level": 1,
            "experience": 0
        }


# Основна сторінка програми
def main_page(page, max_log_length, user_status, log_panel):
    user_data = load_user_data()  # Завантажуємо дані користувача

    # Функція для навігації до сторінки особистого розвитку
    def navigate_to_personal_development(_):
        personal_development_page(page, lambda: main_page(page, max_log_length, user_status, log_panel))

    # Функція для навігації до сторінки навчання
    def navigate_to_education(_):
        education_page(page, lambda: main_page(page, max_log_length, user_status, log_panel))

    # Функція для навігації до сторінки спорту
    def navigate_to_sport(_):
        sport_page(page, lambda: main_page(page, max_log_length, user_status, log_panel))

    # Функція для навігації до сторінки з деталями користувача
    def navigate_to_user_details():
        user_details_page(page, lambda: main_page(page, max_log_length, user_status, log_panel),
                          user_data)

    # Створення заголовка
    header = create_header()

    # Створення статусу користувача з можливістю переходу на сторінку деталей
    user_status = create_user_status(navigate_to_user_details)

    # Модуль для кнопок навігації
    module_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("📜 Модулі розвитку", size=20, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.ElevatedButton("Особистий розвиток", icon=ft.icons.TRENDING_UP,
                                          on_click=navigate_to_personal_development),
                        ft.ElevatedButton("Навчання", icon=ft.icons.SCHOOL, on_click=navigate_to_education),
                        ft.ElevatedButton("Спорт", icon=ft.icons.SPORTS_VOLLEYBALL, on_click=navigate_to_sport),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    wrap=True,
                ),
            ],
            spacing=10,
        ),
        padding=20,
        margin=10,
        bgcolor="#3E3E56",  # Фон контейнера
        border_radius=15,   # Радіус скруглення
        expand=True,        # Розширює контейнер
    )

    # Створення інтерфейсу для введення команд користувачем
    user_input = create_user_input(
        lambda command: process_command(command, log_panel, max_log_length)
    )

    # Очищаємо сторінку і додаємо на неї елементи
    page.clean()
    page.add(
        ft.Column(
            [
                header,  # Додаємо заголовок
                ft.Row([user_status, module_panel], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),  # Додаємо статус та модуль
                ft.Row([log_panel], alignment=ft.MainAxisAlignment.CENTER),  # Додаємо панель журналу
                user_input,  # Додаємо поле для вводу команд
            ],
            spacing=20,
            expand=True,
        )
    )


# Функція для запуску програми
def main(page: ft.Page):
    page.title = "Асистент у стилі RPG"  # Назва вікна
    page.theme_mode = "light"  # Тема програми
    page.padding = 10  # Відступи
    page.bgcolor = "#1E1E2E"  # Колір фону
    page.window_width = 800  # Ширина вікна
    page.window_height = 550  # Висота вікна
    page.window_min_width = 510  # Мінімальна ширина вікна
    page.window_min_height = 500  # Мінімальна висота вікна
    page.window_max_width = 900  # Максимальна ширина вікна
    page.window_max_height = 800  # Максимальна висота вікна

    max_log_length = 5  # Максимальна кількість записів у журналі

    log_panel = create_log_panel()  # Створення панелі для журналу

    # Перехід на основну сторінку
    main_page(page, max_log_length, None, log_panel)


ft.app(target=main)  # Запуск програми
