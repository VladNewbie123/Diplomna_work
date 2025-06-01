import flet as ft
from db import get_all_subjects, get_topics_by_subject, get_materials_by_topic, \
    get_quiz_by_topic, get_questions_and_answers, saves_quiz_result, \
    get_user_education, update_education_status
from pages.user_details_page import update_characteristics


def education_page(page, back_to_main, user_id):
    # Функция рендерит список всех предметов (разделов обучения)
    def render_subjects():
        subjects = get_all_subjects()  # Получаем список всех предметов из БД
        return ft.Row(
            [
                # Для каждого предмета создаем кнопку с названием,
                # при нажатии на которую показываются темы этого предмета
                ft.ElevatedButton(sub[1], on_click=lambda e, s=sub: show_topics(s))
                for sub in subjects
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
        )

    # Показывает список тем по выбранному предмету
    def show_topics(subject):
        subject_id, subject_name, _ = subject
        topics = get_topics_by_subject(subject_id)  # Получаем темы для предмета
        user_education = get_user_education(user_id) or []  # Получаем прогресс пользователя

        progress_by_topic = {}
        # Анализируем прогресс по каждой теме (сколько тестов пройдено)
        for row in user_education:
            _, uid, topic_id, test_passed, materials_unlocked, _, quiz_block = row
            if topic_id not in progress_by_topic:
                progress_by_topic[topic_id] = {"passed_blocks": 0}
            if test_passed:
                progress_by_topic[topic_id]["passed_blocks"] += 1

        page.clean()  # Очищаем страницу
        page.add(
            ft.Column(
                [
                    ft.Text(f"Теми з {subject_name}", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                    ft.Divider(color="#FFD700", thickness=1),
                    # Кнопки с темами и прогрессом по ним
                    *[
                        ft.ElevatedButton(
                            f"{topic[2]} ({progress_by_topic.get(topic[0], {}).get('passed_blocks', 0)}/3)",
                            on_click=lambda e, t=topic: show_materials(subject, t)
                        )
                        for topic in topics
                    ],
                    ft.ElevatedButton("Назад", on_click=lambda _: back_to_main())
                ],
                spacing=20,
                expand=True
            )
        )

    # Показывает учебные материалы и тесты для выбранной темы
    def show_materials(subject, topic):
        subject_id, subject_name, _ = subject
        topic_id, _, topic_name, topic_desc, level = topic

        all_materials = get_materials_by_topic(topic_id)  # Получаем материалы темы
        quiz = get_quiz_by_topic(topic_id)  # Получаем тест для темы
        user_education = get_user_education(user_id) or []  # Прогресс пользователя

        progress_by_topic = {}
        # Формируем словарь с информацией о пройденных тестах по блокам
        for row in user_education:
            _, uid, t_id, test_passed, materials_unlocked, _, quiz_block = row
            if t_id not in progress_by_topic:
                progress_by_topic[t_id] = {}
            progress_by_topic[t_id][quiz_block] = test_passed

        topic_progress = progress_by_topic.get(topic_id, {})

        # Делим все материалы на 3 блока (для прохождения поэтапно)
        blocks = [all_materials[i::3] for i in range(3)]
        user_answers = {}  # Словарь для ответов пользователя на вопросы

        # Обработка выбора ответа пользователем
        def on_answer_selected(e, question_id):
            answer_id = int(e.control.value)
            user_answers[question_id] = answer_id

        # Обработка завершения теста для блока
        def submit_quiz(e, block_index):
            block_size = 1  # Размер блока (кол-во вопросов)
            start = block_index * block_size
            end = start + block_size
            all_questions = get_questions_and_answers(quiz[0])  # Получаем все вопросы
            difficulty_order = {'початковий': 1, 'середній': 2, 'високий': 3}
            # Сортируем вопросы по уровню сложности
            all_questions = sorted(all_questions,
                                   key=lambda q: difficulty_order.get(q.get('difficulty_level', 'початковий'), 1))
            block_questions = all_questions[start:end]

            score = 0
            # Подсчитываем количество правильных ответов
            for q in block_questions:
                correct = next((a for a in q["answers"] if a["is_correct"]), None)
                if correct and user_answers.get(q["question_id"]) == correct["answer_id"]:
                    score += 1

            # Проверяем, прошел ли пользователь тест (70% и выше)
            passed = score >= (len(block_questions) * 0.7)
            saves_quiz_result(user_id, quiz[0], score, passed)  # Сохраняем результат теста

            # Обновляем статус обучения в БД
            update_education_status(user_id, topic_id, test_passed=passed, materials_unlocked=True, quiz_block=block_index)

            # Показываем результат и обновляем характеристики пользователя
            show_result(score, len(block_questions), passed, block_index)
            update_characteristics(user_id)

        # Запуск теста (показ вопросов и вариантов ответов)
        def start_quiz(e, block_index):
            page.clean()
            components = [
                ft.Text(f"Тест №{block_index + 1} по темі: {topic_name}", size=24, weight=ft.FontWeight.BOLD,
                        color="#FFD700")
            ]

            block_size = 1
            start = block_index * block_size
            end = start + block_size
            all_questions = get_questions_and_answers(quiz[0])
            difficulty_order = {'початковий': 1, 'середній': 2, 'високий': 3}
            all_questions = sorted(all_questions,
                                   key=lambda q: difficulty_order.get(q.get('difficulty_level', 'початковий'), 1))
            block_questions = all_questions[start:end]

            if not block_questions:
                components.append(ft.Text("Питання для цього блоку не знайдені.", color="red"))
                page.add(ft.Column(components))
                page.update()
                return

            # Отображаем вопросы и радиокнопки с ответами
            for q in block_questions:
                components.append(ft.Text(q["question_text"], size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"))
                radio_buttons = [
                    ft.Radio(value=str(a["answer_id"]), label=a["text"], label_style=ft.TextStyle(color="#FFFFFF"))
                    for a in q["answers"]
                ]
                radio_group = ft.RadioGroup(
                    value="",
                    content=ft.Column(radio_buttons),
                    on_change=lambda e, q_id=q["question_id"]: on_answer_selected(e, q_id)
                )
                components.append(radio_group)

            # Кнопки для завершения теста и возврата к материалам
            components.append(ft.ElevatedButton("Завершити тест", on_click=lambda e: submit_quiz(e, block_index)))
            components.append(ft.ElevatedButton("Назад", on_click=lambda _: show_materials(subject, topic)))

            page.add(ft.Column(components, spacing=15, expand=True))
            page.update()

        # Показывает результат теста: баллы и статус прохождения
        def show_result(score, total, passed, block_index):
            page.clean()
            result_text = ft.Text(f"Тест завершено! Ваш результат: {score} з {total}", size=20, color="#FFFFFF")
            status_text = ft.Text(
                "Ви успішно пройшли тест." if passed else "Ви не пройшли тест.",
                color="#00FF00" if passed else "#FF0000"
            )
            components = [
                result_text,
                status_text,
                ft.ElevatedButton("Пройти ще раз", on_click=lambda e: start_quiz(e, block_index)),
                ft.Divider(thickness=2),
                ft.ElevatedButton("Назад", on_click=lambda _: show_materials(subject, topic))
            ]
            page.add(ft.Column(components, spacing=20, alignment=ft.MainAxisAlignment.CENTER, expand=True))
            page.update()

        page.clean()
        components = [
            ft.Text(f"Навчальні матеріали по {topic_name}", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
            ft.Text(topic_desc or "Опис відсутній.", size=16, color="#FFFFFF"),
        ]

        # Перебираем 3 блока материалов и отображаем их, если предыдущий блок пройден
        for i in range(3):
            prev_passed = i == 0 or topic_progress.get(i - 1) is True
            if prev_passed:
                block_materials = blocks[i]
                if block_materials:
                    components.append(ft.Text(f"Блок {i + 1}", size=20, color="#FFA500", weight=ft.FontWeight.BOLD))
                    for mat in block_materials:
                        components.append(ft.Text(f"• {mat[2]}", size=16, color="#FFFFFF"))
                    passed = topic_progress.get(i, False)
                    test_status = "✅ Пройдено" if passed else "❌ Не пройдено"
                    components.append(
                        ft.ElevatedButton(f"Тест до блоку {i + 1} ({test_status})", on_click=lambda e, i=i: start_quiz(e, i)))
                    components.append(ft.Divider(color="#555555"))
            else:
                # Блок заблокирован пока не пройден предыдущий
                components.append(ft.Text(f"Блок {i + 1} буде доступний після проходження попереднього тесту.",
                                          size=16, color="#888888", italic=True))

        components.append(ft.ElevatedButton("Назад", on_click=lambda _: show_topics(subject)))
        page.add(ft.Column(components, spacing=15, expand=True))
        page.update()

    # Главная страница обучения: выбор предмета
    def back_to_main_page():
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Виберіть предмет для навчання", size=30, color="#FFD700", weight=ft.FontWeight.BOLD),
                    ft.Divider(color="#FFD700", thickness=1),
                    render_subjects(),  # Показываем кнопки с предметами
                    ft.ElevatedButton("Назад", on_click=lambda _: back_to_main()),
                ],
                spacing=20,
                expand=True
            )
        )

    back_to_main_page()  # Показываем главную страницу с предметами при запуске
