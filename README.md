# Company Org API

API для управления организационной структурой компании (подразделения и сотрудники) в соответствии с тестовым заданием «API организационной структуры».  
Проект реализован на FastAPI с использованием PostgreSQL, SQLAlchemy, Alembic и Docker.

## Функциональные возможности

- Управление подразделениями (Department) с произвольной глубиной вложенности (дерево через `parent_id`).  
- Управление сотрудниками (Employee), привязанными к подразделениям.  
- Создание, обновление и удаление подразделений.
- Создание сотрудников внутри конкретного подразделения.
- Получение подразделения с:
  - его деталями,
  - списком сотрудников,
  - поддеревом дочерних подразделений до указанной глубины `depth`.  
- Перемещение подразделения в другое (смена родителя) с защитой от циклов.  
- Удаление подразделения:
  - с каскадным удалением дочерних подразделений и сотрудников (`mode=cascade`),
  - с перевыставлением сотрудников в другое подразделение (`mode=reassign`).  

## Стек технологий

- Python 3.13
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker, docker-compose
- Pydantic (FastAPI)

## Модели данных

### Department — подразделение

- `id: int` — первичный ключ.
- `name: str` — название подразделения, не пустое, длина 1..200, уникально в пределах одного родителя.  
- `parent_id: int | null` — внешний ключ на `Department.id`, задаёт иерархию.  
- `created_at: datetime` — дата и время создания записи.

Дополнительно:

- Самоссылочная связь `Department` 1‑N `Department` через `parent_id`.  
- Ограничение уникальности имени в пределах одного `parent_id` (например, два `"Backend"` под одним родителем запрещены).  

### Employee — сотрудник

- `id: int` — первичный ключ.
  - `department_id: int` — внешний ключ на `Department.id`.  
- `full_name: str` — ФИО, не пустое, длина 1..200.  
- `position: str` — должность, не пустая, длина 1..200.  
- `hired_at: date | null` — дата найма (опционально).  
- `created_at: datetime` — дата и время создания записи.

Связи:

- `Department` 1‑N `Employee`.  

## Бизнес‑логика и ограничения

- Нельзя создать сотрудника в несуществующем подразделении — возвращается 404.  
- Название подразделения:
  - не пустое, длина 1..200,
  - может проходить тримминг пробелов по краям,
  - уникально в пределах одного родителя.  
- `full_name` и `position` сотрудника — не пустые, длина 1..200.  
- Нельзя сделать подразделение родителем самого себя.  
- Нельзя создать цикл в дереве (переместить департамент внутрь собственного поддерева) — возвращается 400/409.  
- `GET /departments/{id}` корректно отдаёт поддерево до глубины `depth` (по умолчанию 1, максимум 5).  
- При удалении в режиме `cascade` каскадное удаление настроено на уровне БД/ORM для подразделений и сотрудников.  

## Методы API

Ниже краткое описание основных эндпоинтов в терминах ТЗ.  

### 1) Создать подразделение

**POST** `/departments/`

Body:

```json
{
  "name": "Backend",
  "parent_id": 1
}
```

Ответ: созданное подразделение с полями `id`, `name`, `parent_id`, `created_at`.

### 2) Создать сотрудника в подразделении

**POST** `/departments/{id}/employees/`

Body:

```json
{
  "full_name": "Иванов Иван Иванович",
  "position": "Backend Developer",
  "hired_at": "2024-01-01"
}
```

Где `{id}` — идентификатор существующего подразделения.  

Ответ: созданный сотрудник с полями `id`, `department_id`, `full_name`, `position`, `hired_at`, `created_at`.

### 3) Получить подразделение (детали + сотрудники + поддерево)

**GET** `/departments/{id}`

Query‑параметры:

- `depth: int` — глубина вложенных подразделений (по умолчанию 1, максимум 5).  
- `include_employees: bool` — включать ли сотрудников (по умолчанию `true`).  

Пример ответа:

```json
{
  "id": 1,
  "name": "Head Office",
  "parent_id": null,
  "created_at": "...",
  "employees": [
    {
      "id": 10,
      "full_name": "Иванов Иван Иванович",
      "position": "Backend Developer",
      "hired_at": "2024-01-01",
      "created_at": "..."
    }
  ],
  "children": [
    {
      "id": 2,
      "name": "Backend",
      "parent_id": 1,
      "created_at": "...",
      "employees": [],
      "children": []
    }
  ]
}
```

Сотрудники внутри подразделения могут сортироваться по `created_at` или `full_name`.  

### 4) Переместить подразделение в другое (изменить parent)

**PATCH** `/departments/{id}`

Body (любые поля опциональны):

```json
{
  "name": "Backend Team",
  "parent_id": 3
}
```

Логика:

- Если указан `parent_id`, выполняется проверка на отсутствие циклов в дереве.  
- Нельзя установить родителем самого себя или потомка.  

Ответ: обновлённое подразделение.

### 5) Удалить подразделение

**DELETE** `/departments/{id}`

Query‑параметры:

- `mode: str` — `"cascade"` или `"reassign"`.  
- `reassign_to_department_id: int` — обязательно, если `mode=reassign`.  

Режимы:

- `cascade` — удалить подразделение, всех его сотрудников и все дочерние подразделения каскадно.  
- `reassign` — удалить подразделение, а сотрудников перевести в `reassign_to_department_id`.  

Ответ: `204 No Content` или JSON со статусом операции.

## Документация API (OpenAPI)

Документация генерируется автоматически на основе схем FastAPI и доступна по адресам:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Архитектура проекта

Пример структуры каталогов:

```text
.
├── app
│   ├── main.py                # Точка входа FastAPI
│   ├── api
│   │   └── v1
│   │       ├── departments.py # HTTP-эндпоинты для департаментов
│   │       └── employees.py   # HTTP-эндпоинты для сотрудников
│   ├── core
│   │   ├── config.py          # Настройки, работа с env, DATABASE_URL
│   │   └── db.py              # Подключение к БД, sessionmaker
│   ├── models
│   │   ├── department.py      # SQLAlchemy-модель Department
│   │   └── employee.py        # SQLAlchemy-модель Employee
│   ├── repositories
│   │   ├── department.py      # Логика работы с департаментами (CRUD, дерево)
│   │   └── employee.py        # Логика работы с сотрудниками
│   └── schemas
│       ├── department.py      # Pydantic-схемы для департаментов
│       └── employee.py        # Pydantic-схемы для сотрудников
├── alembic
│   ├── env.py
│   └── versions               # Миграции (создание таблиц и связей)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

Принципы:

- Разделение слоёв: API‑роуты → репозитории → модели БД.
- Валидация и сериализация через Pydantic‑схемы.
- Логика работы с деревом и каскадами вынесена в репозитории, а не в контроллеры.

## Запуск проекта

### Запуск через Docker (рекомендуемый способ)

Требования:

- Установлены Docker и Docker Compose.

Шаги:

1. Создать файл `.env` в корне проекта:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=orgdb
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

2. Собрать и запустить контейнеры:

```bash
docker compose up --build
```

3. Открыть в браузере:

- `http://localhost:8000/docs` — документация API.
- Прямые запросы к API, например:
  - `GET http://localhost:8000/departments`
  - `POST http://localhost:8000/departments/`

PostgreSQL будет доступен на `localhost:5432`, приложение — на `localhost:8000`.

### Локальный запуск (без Docker)

Требования:

- Python 3.13
- PostgreSQL

Шаги:

1. Создать и активировать виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Создать базу данных `orgdb` в PostgreSQL и настроить `.env`:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=orgdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

4. Применить миграции Alembic:

```bash
alembic upgrade head
```

5. Запустить приложение:

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу `http://localhost:8000`.

## Миграции БД (Alembic)

- Базовая миграция создаёт таблицы `departments`, `employees` и `alembic_version`, включая:
  - самоссылочный внешний ключ `departments.parent_id → departments.id` с `ON DELETE CASCADE`,
  - внешний ключ `employees.department_id → departments.id` с `ON DELETE CASCADE`,
  - уникальное ограничение на `(parent_id, name)` для департаментов.  

Основные команды:

```bash
alembic upgrade head
alembic revision --autogenerate -m "some message"
```

## Docker и docker-compose

### Dockerfile

- Образ основан на `python:3.13-slim`.
- Устанавливаются зависимости из `requirements.txt`.
- Копируется исходный код в контейнер.
- Приложение запускается через uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### docker-compose.yml

- Сервис `db`:
  - образ `postgres:16`,
  - переменные окружения `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`,
  - проброс порта `5432:5432`,
  - volume для сохранения данных.
- Сервис `app`:
  - собирается из Dockerfile в корне,
  - использует `.env` для конфигурации БД,
  - пробрасывает порт `8000:8000`,
  - зависит от `db` (`depends_on`).
## Тесты

В проекте используется `pytest` и встроенный `TestClient` FastAPI для интеграционного тестирования эндпоинтов.
Добавлен тест для `POST /departments/`, который проверяет корректное создание подразделения и обработку конфликта уникальности имени.  

Запуск тестов внутри Docker‑контейнера:

```bash
docker compose exec app pytest

