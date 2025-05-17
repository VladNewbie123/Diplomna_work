import flet as ft
from datetime import datetime
import random

# Список жартів
jokes = [
    "Чому програмісти не люблять природу? — Бо там багато багів.",
    "Я б розповів ще один жарт про баги, але він іноді не працює.",
    "Як називається фобія видалення коду? — Delete-обія."
]

# Список цитат
quotes = [
    "«Єдиний спосіб зробити велику роботу — це любити те, що ви робите.» — Стів Джобс",
    "«Навчання — це не наповнення відра, а запалювання вогню.» — Вільям Батлер Єйтс",
    "«Успіх — це не випадковість, а результат важкої праці.» — Колін Пауелл"
]

# Відповіді міні-чат-бота
mini_chat_responses = {
    "привіт": "Привіт! Як настрій? 😊",
    "як справи?": "Усе чудово! А в тебе? 😄",
    "мені сумно": "Не засмучуйся! Все налагодиться. 💛",
    "хто ти?": "Я — твій асистент. Питай усе, що цікавить!",
    "що робиш?": "Чекаю твоїх команд. 🤖",
    "дякую": "Завжди радий допомогти! 🙌",
    "до побачення": "Бувай! Гарного дня! 👋"
}

# Функція для додавання повідомлення до логу
def add_to_log(message, log_panel, max_log_length, color):
    timestamp = datetime.now().strftime("[%H:%M:%S]")  # Створення мітки часу
    log_panel.content.controls.append(ft.Text(f"{timestamp} {message}", color=color))  # Додавання повідомлення до логу
    # Перевірка, чи не перевищує кількість повідомлень максимальний ліміт
    while len(log_panel.content.controls) > max_log_length:
        log_panel.content.controls.pop(0)  # Видалення найстарішого повідомлення
    log_panel.update()

# Функція для обробки команд і повідомлень
def process_command(command, log_panel, max_log_length):
    command = command.lower().strip()  # Перетворення команди в нижній регістр і видалення зайвих пробілів

    if not command:  # Якщо команда пуста
        add_to_log("⚠️ Введіть команду або повідомлення!", log_panel, max_log_length, color="#FF4500")
        return

    # Словник стандартних команд
    commands = {
        "факт": "Факт: Людина може жити без їжі до 3 тижнів.",
        "допомога": "Команди: факт, допомога, час, дата, жарт, цитата, очистити.",
        "час": f"Поточний час: {datetime.now().strftime('%H:%M:%S')}",  # Показ поточного часу
        "дата": f"Сьогоднішня дата: {datetime.now().strftime('%d-%m-%Y')}",  # Показ поточної дати
        "жарт": random.choice(jokes),  # Вибір випадкового жарту
        "цитата": random.choice(quotes),  # Вибір випадкової цитати
        "очистити": "Лог очищено."  # Очищення логу
    }

    # Додавання команди користувача в лог
    add_to_log(f"Ви: {command}", log_panel, max_log_length, color="#FFFFFF")

    # Обробка команди "очистити"
    if command == "очистити":
        log_panel.content.controls.clear()  # Очищення всіх повідомлень у логу
        log_panel.update()
        return

    # Перевірка стандартних команд
    if command in commands:
        response = commands[command]
        response_color = "#FFD700"
    # Перевірка міні-чат-бота
    elif command in mini_chat_responses:
        response = mini_chat_responses[command]
        response_color = "#90EE90"
    else:  # Якщо команда не знайдена
        response = "❌ Команда не розпізнана. Спробуйте ще раз або введіть 'допомога'."
        response_color = "#FF4500"

    # Виведення відповіді в лог
    add_to_log(f"Система: {response}", log_panel, max_log_length, color=response_color)
