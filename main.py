# Імпортуємо необхідні модулі з бібліотеки Flet і власні сторінки та компоненти
import flet as ft
from pages.admin import admin_page  # Сторінка адміністратора
from pages.user_details_page import user_details_page, update_characteristics  # Сторінка деталей користувача та функція оновлення характеристик
from pages.personal_development_page import personal_development_page  # Сторінка особистого розвитку
from pages.education_page import education_page  # Сторінка навчання
from pages.sport_page import sport_page  # Сторінка спорту
from ui_components import create_header, create_user_status, create_log_panel, create_user_input  # UI-компоненти
from logic import process_command  # Обробка команд користувача
from db import load_user_data, is_admin  # Завантаження даних користувача та перевірка на адміністратора
from pages.auth_page import get_auth_page  # Сторінка авторизації


# Основна сторінка програми після входу користувача
def main_page(page, max_log_length, user_status, log_panel, user_id):
    user_data = load_user_data(user_id)  # Завантажуємо дані користувача з бази
    update_characteristics(user_id)  # Оновлюємо характеристики користувача

    # Функції переходу до відповідних сторінок
    def navigate_to_personal_development(_):  # Перехід на сторінку особистого розвитку
        personal_development_page(page, lambda: main_page(page, max_log_length, user_status, log_panel, user_id),
                                  user_id)

    def navigate_to_education(_):  # Перехід на сторінку навчання
        education_page(page, lambda: main_page(page, max_log_length, user_status, log_panel, user_id), user_id)

    def navigate_to_sport(_):  # Перехід на сторінку спорту
        sport_page(page, lambda: main_page(page, max_log_length, user_status, log_panel, user_id), user_id)

    def navigate_to_user_details():  # Перехід на сторінку деталей користувача
        user_details_page(page, lambda: main_page(page, max_log_length, user_status, log_panel, user_id),
                          user_data)

    # Створення заголовка програми
    header = create_header()

    # Створення статусу користувача (наприклад, ім’я, рівень тощо)
    user_status = create_user_status(user_id, navigate_to_user_details)

    # Блок з кнопками для переходу до модулів розвитку
    module_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("📜 Модулі розвитку", size=20, color="#FFFFFF", weight=ft.FontWeight.BOLD),  # Назва модуля
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
        bgcolor="#3E3E56",  # Темне тло
        border_radius=15,  # Закруглені кути
        expand=True,  # Розширення блоку по ширині
    )

    # Поле введення команд користувачем (наприклад, "зберегти", "статус")
    user_input = create_user_input(
        lambda command: process_command(command, log_panel, max_log_length)
    )

    # Очищення сторінки та додавання нових елементів
    page.clean()
    page.add(
        ft.Column(
            [
                header,  # Додаємо заголовок
                ft.Row([user_status, module_panel], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),  # Статус + модулі
                ft.Row([log_panel], alignment=ft.MainAxisAlignment.CENTER),  # Панель логів (журналу подій)
                user_input,  # Поле вводу команди
            ],
            spacing=20,
            expand=True,
        )
    )


# Головна функція запуску додатку
def main(page: ft.Page):
    # Налаштування вікна програми
    page.title = "Асистент у стилі RPG"
    page.theme_mode = "light"  # Світла тема
    page.padding = 10
    page.bgcolor = "#1E1E2E"  # Темний фон
    page.window_width = 800
    page.window_height = 550
    page.window_min_width = 510
    page.window_min_height = 500
    page.window_max_width = 900
    page.window_max_height = 800

    max_log_length = 5  # Максимальна кількість рядків у журналі подій
    log_panel = create_log_panel()  # Створюємо панель журналу

    # Колбек після успішного входу
    def on_login_success(user_id):
        page.clean()

        if is_admin(user_id):  # Якщо це адміністратор — відкриваємо адмінську сторінку
            admin_page(page)
        else:  # Інакше — головну сторінку користувача
            main_page(page, max_log_length, None, log_panel, user_id)

    # Початкова сторінка авторизації
    page.clean()
    page.add(get_auth_page(on_login_success))
    page.update()


# Запуск додатку
ft.app(target=main)
