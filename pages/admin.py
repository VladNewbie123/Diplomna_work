import flet as ft
from db import load_all_users, delete_user  # Імпорт функцій для роботи з базою: завантаження та видалення користувачів


def admin_page(page: ft.Page):
    users_data = load_all_users()  # Завантажуємо усіх користувачів з бази даних
    user_controls = []  # Список елементів інтерфейсу для відображення користувачів

    # Функція оновлення списку користувачів, з можливістю сортування за типом
    def refresh_user_list(filter_type=None):
        user_controls.clear()  # Очищуємо поточний список елементів

        # Якщо вибрано сортування за ім'ям — сортуємо, інакше залишаємо порядок як є
        filtered_users = sorted(users_data, key=lambda x: x['name']) if filter_type == "name" else users_data

        # Обмеження відображення — максимум 3 користувачі
        limited_users = filtered_users[:3]

        for user in limited_users:
            user_controls.append(
                ft.Container(
                    content=ft.Column([

                        # Рядок із іменем користувача та кнопкою "Видалити"
                        ft.Row([
                            ft.Icon(name=ft.icons.PERSON, color=ft.colors.WHITE),
                            ft.Text(f"Ім'я: {user['name']}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.ElevatedButton("Видалити", color=ft.colors.BLUE,
                                              on_click=lambda e, uid=user['id']: remove_user(uid))  # Виклик функції видалення з id користувача
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        # Рядок із рівнем і досвідом користувача
                        ft.Row([
                            ft.Icon(name=ft.icons.LEADERBOARD, color=ft.colors.WHITE),
                            ft.Text(f"Рівень: {user.get('level', 0)}", color=ft.colors.WHITE),
                            ft.Icon(name=ft.icons.STAR, color=ft.colors.WHITE),
                            ft.Text(f"Досвід: {user.get('experience', 0)}", color=ft.colors.WHITE),
                        ], spacing=10),

                        # Рядок із характеристиками користувача (сила, інтелект, швидкість, витривалість, баланс)
                        ft.Row([
                            ft.Icon(name=ft.icons.FITNESS_CENTER, color=ft.colors.WHITE),
                            ft.Text(f"Сила: {user.get('strength', 0)}", color=ft.colors.WHITE),
                            ft.Icon(name=ft.icons.PSYCHOLOGY, color=ft.colors.WHITE),
                            ft.Text(f"Інтелект: {user.get('intelligence', 0)}", color=ft.colors.WHITE),
                            ft.Icon(name=ft.icons.SPEED, color=ft.colors.WHITE),
                            ft.Text(f"Швидкість: {user.get('speed', 0)}", color=ft.colors.WHITE),
                            ft.Icon(name=ft.icons.FAVORITE, color=ft.colors.WHITE),
                            ft.Text(f"Витривалість: {user.get('endurance', 0)}", color=ft.colors.WHITE),
                            ft.Icon(name=ft.icons.ACCESSIBILITY, color=ft.colors.WHITE),
                            ft.Text(f"Баланс: {user.get('balance', 0)}", color=ft.colors.WHITE),
                        ], spacing=10),

                    ]),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.08, ft.colors.BLUE_GREY),  # Фон контейнера з прозорістю
                    border_radius=10  # Закруглення кутів контейнера
                )
            )

        # Оновлення колонки з користувачами на сторінці
        users_column.controls = user_controls
        page.update()  # Оновлення сторінки для відображення змін

    # Функція видалення користувача за ID
    def remove_user(uid):
        delete_user(uid)  # Видаляємо користувача з бази даних
        page.snack_bar = ft.SnackBar(ft.Text("Користувача видалено"))  # Показуємо сповіщення про успішне видалення
        page.snack_bar.open = True

        # Оновлюємо локальний список користувачів, виключаючи видаленого
        new_list = [u for u in users_data if u['id'] != uid]
        users_data.clear()
        users_data.extend(new_list)
        refresh_user_list()  # Оновлюємо список на сторінці

    users_column = ft.Column()  # Створюємо колонку для виводу користувачів

    page.clean()  # Очищаємо сторінку перед додаванням нового вмісту
    page.add(
        ft.Column([
            ft.Text("👮 Панель адміністратора", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),

            # Рядок з кнопками сортування
            ft.Row([
                ft.Text("Сортувати:", color=ft.colors.WHITE),
                ft.ElevatedButton("🔠 За ім’ям", color=ft.colors.BLUE, on_click=lambda e: refresh_user_list("name")),
                ft.ElevatedButton("🏆 За рівнем", color=ft.colors.BLUE, on_click=lambda e: refresh_user_list("level")),
            ]),

            ft.Divider(color=ft.colors.WHITE),
            users_column,  # Колонка з користувачами, сюди додаються елементи
            ft.Divider(color=ft.colors.WHITE),
        ],
            scroll=ft.ScrollMode.AUTO,  # Додаємо прокрутку, якщо контент більший за екран
            spacing=15)
    )

    refresh_user_list()  # Ініціалізуємо початкове завантаження користувачів
