import flet as ft
import json


# Функція для перечитування user_data.json
def reload_user_data():
    with open("user_data.json", "r", encoding="utf-8") as file:
        return json.load(file)


# Функція для збереження даних в user_data.json
def save_user_data(user_data, file_path='user_data.json'):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(user_data, file, indent=4, ensure_ascii=False)


# Функція для оновлення даних по вибраному навчальному напрямку
def update_education_data(user_data, subject, topic, materials, is_material_learned):
    if "education" not in user_data:
        user_data["education"] = {}

    if subject not in user_data["education"]:
        user_data["education"][subject] = {}

    user_data["education"][subject][topic] = {"materials": materials, "is_learned": is_material_learned}
    save_user_data(user_data)


# Функція для отримання інформації з локального JSON файлу
def get_topic_info(subject, topic):
    try:
        with open("subjects_data.json", "r", encoding="utf-8") as file:
            subjects_data = json.load(file)

        if subject in subjects_data and topic in subjects_data[subject]:
            return subjects_data[subject][topic]
        else:
            return f"Інформація по темі '{topic}' не знайдена."

    except Exception as e:
        return f"Сталася помилка при читанні файлу: {str(e)}"


# Основна сторінка вибору предмету та теми
def education_page(page, back_to_main):
    # Завантажуємо всі предмети з файлу subjects_data.json
    def load_subjects():
        try:
            with open("subjects_data.json", "r", encoding="utf-8") as file:
                subjects_data = json.load(file)
                return {subject: list(topics.keys()) for subject, topics in subjects_data.items()}
        except Exception as e:
            return {}

    subjects = load_subjects()  # Отримуємо список всіх предметів та їхніх тем

    # Функція для відображення списку предметів
    def render_subjects():
        return ft.Row(
            [
                ft.ElevatedButton(subject, on_click=lambda e, s=subject: show_topics(s))
                for subject in subjects.keys()
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
        )

    # Функція для відображення списку тем вибраного предмета
    def show_topics(subject):
        topics = subjects.get(subject, [])  # Отримуємо список тем для вибраного предмета
        page.clean()  # Очищаємо поточну сторінку
        page.add(
            ft.Column(
                [
                    ft.Text(f"Теми з {subject}", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                    ft.Divider(color="#FFD700", thickness=1),
                    *[ft.ElevatedButton(topic, on_click=lambda e, t=topic: show_materials(subject, t)) for topic in
                      topics],
                    ft.ElevatedButton("Назад", on_click=lambda _: back_to_main()),
                ],
                spacing=20,
                expand=True
            )
        )

    # Функція для відображення навчальних матеріалів по вибраній темі
    def show_materials(subject, topic):
        materials = get_topic_info(subject, topic)  # Отримуємо інформацію з локального файлу
        updated_data = reload_user_data()

        # Перевіряємо стан усвідомлення теми
        is_material_learned = updated_data.get("education", {}).get(subject, {}).get(topic, {}).get("is_learned", False)

        # Галочка для підтвердження усвідомлення
        checkbox_checked = is_material_learned
        checkbox = ft.Checkbox(label="Усвоїв матеріал", value=checkbox_checked,
                               on_change=lambda e: save_materials(subject, topic, materials, e.control.value))

        page.clean()  # Очищаємо поточну сторінку
        page.add(
            ft.Column(
                [
                    ft.Text(f"Навчальні матеріали по {topic}", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                    ft.Text(materials["info"], size=16, color="#FFFFFF"),

                    # Заміна "формул" на більш універсальний термін
                    ft.Text(
                        f"{'Формули' if subject in ['Математика', 'Фізика'] else 'Основні моменти'}: {', '.join(materials.get('formulas', materials.get('key_points', [])))}",
                        size=16, color="#FFFFFF"),

                    checkbox,
                    ft.ElevatedButton("Назад", on_click=lambda _: show_topics(subject)),
                ],
                spacing=20,
                expand=True
            )
        )

    # Функція для збереження стану усвідомлення навчальних матеріалів
    def save_materials(subject, topic, materials, is_material_learned):
        updated_data = reload_user_data()
        update_education_data(updated_data, subject, topic, materials, is_material_learned)
        ft.Toast("Стан усвідомлення збережено", duration=2000).show()

    # Відображення головної сторінки вибору предметів
    def back_to_main_page():
        page.clean()  # Очищаємо поточну сторінку
        page.add(
            ft.Column(
                [
                    ft.Text("Виберіть предмет для навчання", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                    ft.Divider(color="#FFD700", thickness=1),
                    render_subjects(),
                    ft.ElevatedButton("Назад", on_click=lambda _: back_to_main()),
                ],
                spacing=20,
                expand=True
            )
        )

    # Запуск головної сторінки вибору предметів
    back_to_main_page()
