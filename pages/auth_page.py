import flet as ft
from db import get_user_by_username, create_user, verify_password

# Відповідність назви ролі до її ID в базі даних
ROLE_MAP = {
    "user": 1,
    "admin": 2
}


def get_auth_page(on_login_success):
    # --- Стан ---
    mode = {"value": "login"}  # або "register"

    # --- Елементи інтерфейсу ---
    username_field = ft.TextField(label="Ім’я користувача", color="#FFFFFF", border_color="#FFD700",
                                  label_style=ft.TextStyle(color="#B0B0B0"))
    password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True, color="#FFFFFF",
                                  border_color="#FFD700", label_style=ft.TextStyle(color="#B0B0B0"))
    message_text = ft.Text("", color="red", size=20)

    role_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Text("Оберіть роль:", color="white", weight=ft.FontWeight.BOLD, size=25),
            ft.Radio(value="user", label="Користувач", fill_color="white", label_style=ft.TextStyle(color="#B0B0B0")),
            ft.Radio(value="admin", label="Адміністратор", fill_color="white",
                     label_style=ft.TextStyle(color="#B0B0B0")),
        ]),
        value="user",
        visible=False  # спочатку приховано (для реєстрації)
    )

    # --- Кнопки ---
    login_button = ft.ElevatedButton("Увійти", on_click=lambda e: handle_login(e), visible=True)
    register_button = ft.ElevatedButton("Зареєструватися", on_click=lambda e: handle_register(e), visible=False)

    def switch_mode(e, new_mode):
        mode["value"] = new_mode
        is_register = new_mode == "register"
        role_radio.visible = is_register
        login_button.visible = not is_register
        register_button.visible = is_register
        message_text.value = ""
        e.page.update()

    # --- Логіка входу ---
    def handle_login(e):
        username = username_field.value.strip()
        password = password_field.value.strip()

        if not username or not password:
            message_text.value = "Заповніть усі поля"
            e.page.update()
            return

        user = get_user_by_username(username)
        if user and verify_password(password, user["password_hash"]):
            role_id = user.get("role_id", 1)
            role_name = [name for name, id in ROLE_MAP.items() if id == role_id][0]

            e.page.session.set("user_id", user["id"])
            e.page.session.set("username", username)
            e.page.session.set("role", role_name)

            if role_name == "admin":
                e.page.session.set("next_route", "/admin_dashboard")
            else:
                e.page.session.set("next_route", "/user_dashboard")

            on_login_success(user["id"])
        else:
            message_text.value = "Невірне ім’я користувача або пароль"
            e.page.update()

    # --- Логіка реєстрації ---
    def handle_register(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        selected_role = role_radio.value

        if not username or not password:
            message_text.value = "Заповніть усі поля"
            e.page.update()
            return

        if get_user_by_username(username):
            message_text.value = "Користувач уже існує"
        else:
            role_id = ROLE_MAP.get(selected_role, 1)
            create_user(username, password, role_id)
            message_text.value = "Успішна реєстрація! Тепер увійдіть."
            # автоматичне повернення до логіну
            switch_mode(e, "login")

        e.page.update()

    # --- Головна форма ---
    return ft.Column(
        [
            ft.Text("Вхід / Реєстрація", size=24, weight=ft.FontWeight.BOLD, color="#FFD700"),

            # Кнопки перемикання режимів
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Увійти",
                        on_click=lambda e: switch_mode(e, "login"),
                        bgcolor="#FFD700",
                        color="black",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=20),
                            elevation=5,
                        )
                    ),
                    ft.Text("/"),
                    ft.ElevatedButton(
                        "Зареєструватися",
                        on_click=lambda e: switch_mode(e, "register"),
                        bgcolor="#FFD700",
                        color="black",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=20),
                            elevation=5,
                        )
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER  # Центрування кнопок по горизонталі
            ),

            username_field,
            password_field,
            role_radio,

            # Кнопки підтвердження
            ft.Row([
                login_button,
                register_button
            ], spacing=10),

            message_text
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
