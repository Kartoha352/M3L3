# Бот-портфолио через БД SQLite3

## Описание

Проект "Бот-портфолио" представляет собой приложение, реализованное с использованием SQLite3 для управления и хранения данных. Основная цель этого проекта — создать портфолио-бота, который может взаимодействовать с пользователем и предоставлять информацию о проектах, навыках и достижениях разработчика.

### Основные функции

1. **Хранение данных**: Использование базы данных SQLite3 для хранения информации о проектах, навыках, достижениях и другой связанной информации.
2. **CRUD операции**: Поддержка создания, чтения, обновления и удаления записей в базе данных.
3. **Интерактивное взаимодействие**: Бот может отвечать на запросы пользователя, предоставляя соответствующую информацию из базы данных.

### Архитектура проекта

1. **База данных**: SQLite3 используется для хранения всех данных. Это включает таблицы для проектов, навыков, статусов и связывающей таблицы для проектных навыков.
2. **Telegram-Бот**: Основное приложение, которое взаимодействует с пользователем. Бот принимает запросы, обрабатывает их, взаимодействует с базой данных и возвращает ответы пользователю.
3. **Интерфейс пользователя**: Может быть реализован через консоль, веб-интерфейс или мессенджеры (например, Discord), в зависимости от предпочтений разработчика. Нужно лишь взять логику БД и связать её с вашим интерфейсом.

### Структура базы данных

- **Таблица projects**:
    - `project_id` (INTEGER, PRIMARY KEY)
    - `user_id` (INTEGER)
    - `project_name` (TEXT)
    - `description` (TEXT)
    - `url` (TEXT)
    - `status_id` (INTEGER)

- **Таблица skills**:
    - `skill_id` (INTEGER, PRIMARY KEY)
    - `skill_name` (TEXT)

- **Таблица status**:
    - `status_id` (INTEGER, PRIMARY KEY)
    - `status_name` (TEXT)

- **Таблица project_skills**:
    - `project_id` (INTEGER)
    - `skill_id` (INTEGER)

## Обновления

# **V1.0**:
    - Проект был добавлен.

# **V2.0**:
    - Был обновлён интерфейс всех команд команд.
    - В команде */projects* теперь можно сразу удалять проект при нажатии на соответствующую кнопку.
        ![Logo](images/projects.jpg)
    - В команде */new_project* теперь показывает сразу информацию о проекте чтобы было лучше ориентироваться.
        ![Logo](images/new_project.jpg)
