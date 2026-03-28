# ETL Module 3 — Unified Data Platform Project

Учебный ETL/ELT-проект, объединяющий 4 задания модуля 3 дисциплины «ETL-процессы» в единую data platform.

## Архитектура

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  JSON / XML │     │  CSV (temp)  │     │   MongoDB     │     │  PostgreSQL  │
│  источники  │     │  датасет     │     │  (5 коллекц.) │     │  staging     │
└──────┬──────┘     └──────┬───────┘     └──────┬────────┘     │  dwh         │
       │                   │                    │              │  mart        │
       ▼                   ▼                    ▼              └──────────────┘
  DAG: webinar_2      DAG: webinar_3      DAG: final_generate        │
  flatten → CSV       transform → CSV     → MongoDB                  │
                           │                    │                     │
                           ▼                    ▼                     │
                      DAG: webinar_4       DAG: final_replicate       │
                      full + incremental   staging → dwh ─────────►  │
                      → PostgreSQL              │                     │
                                                ▼                     │
                                          DAG: final_build            │
                                          → mart (витрины) ──────►   │
```

## Источники данных

| Источник | Формат | Описание |
|----------|--------|----------|
| `data/sample/sample_nested.json` | JSON | Вложенная структура: компания → отделы → сотрудники → навыки, проекты |
| `data/sample/sample_nested.xml` | XML | Каталог книг: магазины → категории → книги → теги, отзывы |
| `data/sample/sample_temperature.csv` | CSV | Температурные данные за год (noted_date, temp, out/in) |
| MongoDB (генерация) | BSON | 5 коллекций: user_sessions, event_logs, support_tickets, user_recommendations, moderation_queue |

## DAG-и Airflow

| DAG | Описание | Schedule |
|-----|----------|----------|
| `webinar_2_flatten_sources_dag` | Приведение JSON и XML к табличной структуре | `@once` |
| `webinar_3_transform_weather_dag` | Трансформация температурного датасета: фильтрация, очистка, top-5 дней | `@once` |
| `webinar_4_load_to_postgres_dag` | Загрузка в PostgreSQL: full historical + incremental load | `@once` |
| `final_generate_mongo_data_dag` | Генерация данных в MongoDB (воспроизводимая, seed=42) | `@once` |
| `final_replicate_mongo_to_postgres_dag` | Репликация MongoDB → PostgreSQL (staging → dwh) | `@once` |
| `final_build_datamarts_dag` | Построение аналитических витрин (materialized views) | `@once` |

## Таблицы PostgreSQL

### Схема `staging`
- `weather_raw` — сырые температурные данные
- `sessions`, `session_pages`, `session_actions` — сессии пользователей
- `events` — логи событий
- `tickets`, `ticket_messages` — обращения в поддержку
- `recommendations`, `recommendation_products` — рекомендации
- `moderation_reviews`, `moderation_flags` — модерация отзывов
- `load_state` — watermark для incremental load

### Схема `dwh`
Те же таблицы с нормализованной структурой, PK/FK, индексами. Таблица `events` партиционирована по кварталам.

### Схема `mart`
- `dm_user_activity` — витрина активности пользователей (сессии, время на сайте, популярные страницы/действия, активность по дням/часам)
- `dm_support_efficiency` — витрина эффективности поддержки (тикеты по статусам/типам, время решения, агрегаты по дням/неделям)

## Быстрый старт

### 1. Клонировать и создать `.env`

```bash
git clone <url>
cd etl_module_3_project
cp .env.example .env
```

### 2. Запустить инфраструктуру

```bash
docker-compose up -d
```

Это поднимет:
- **PostgreSQL** (порт 5432) — БД `etl_project`, схемы `staging/dwh/mart`
- **MongoDB** (порт 27017) — БД `etl_source`
- **Airflow Webserver** (порт 8080) — UI: http://localhost:8080 (admin/admin)
- **Airflow Scheduler** — обработка DAG-ов

### 3. Дождаться инициализации

```bash
docker-compose logs -f airflow-init
```

Когда увидите `exited with code 0`, Airflow готов.

### 4. Запустить DAG-и

Откройте Airflow UI → http://localhost:8080, логин: `admin` / `admin`.

**Порядок запуска:**

1. `webinar_2_flatten_sources_dag` — flatten JSON/XML
2. `webinar_3_transform_weather_dag` — трансформация температурных данных
3. `webinar_4_load_to_postgres_dag` — загрузка в PostgreSQL
4. `final_generate_mongo_data_dag` — генерация данных в MongoDB
5. `final_replicate_mongo_to_postgres_dag` — репликация в PostgreSQL
6. `final_build_datamarts_dag` — построение витрин

Каждый DAG можно запустить кнопкой «Trigger DAG» (▶) в UI.

### 5. Проверить результат

**PostgreSQL:**
```bash
docker exec -it etl_module_3_project-postgres-1 psql -U etl_user -d etl_project

-- Проверка DWH
SELECT COUNT(*) FROM dwh.sessions;
SELECT COUNT(*) FROM dwh.events;
SELECT COUNT(*) FROM dwh.tickets;

-- Проверка витрин
SELECT * FROM mart.dm_user_activity LIMIT 10;
SELECT * FROM mart.dm_support_efficiency LIMIT 10;
```

**MongoDB:**
```bash
docker exec -it etl_module_3_project-mongodb-1 mongosh etl_source

db.user_sessions.countDocuments()
db.event_logs.countDocuments()
db.support_tickets.countDocuments()
db.user_recommendations.countDocuments()
db.moderation_queue.countDocuments()
```

## Структура репозитория

```
etl_module_3_project/
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── airflow/
│   ├── dags/
│   │   ├── webinar_2_flatten_sources_dag.py
│   │   ├── webinar_3_transform_weather_dag.py
│   │   ├── webinar_4_load_to_postgres_dag.py
│   │   ├── final_generate_mongo_data_dag.py
│   │   ├── final_replicate_mongo_to_postgres_dag.py
│   │   └── final_build_datamarts_dag.py
│   └── plugins/
├── src/
│   ├── config/
│   │   └── settings.py
│   ├── utils/
│   │   ├── logger.py
│   │   ├── io_helpers.py
│   │   ├── date_helpers.py
│   │   └── db.py
│   ├── webinar_2/
│   │   ├── flatten_json.py
│   │   ├── flatten_xml.py
│   │   └── schemas.py
│   ├── webinar_3/
│   │   ├── transform_weather.py
│   │   └── quality_checks.py
│   ├── webinar_4/
│   │   ├── full_load.py
│   │   ├── incremental_load.py
│   │   └── state_manager.py
│   └── final_project/
│       ├── generate_mongo_data.py
│       ├── mongo_extract.py
│       ├── mongo_transform.py
│       ├── postgres_load.py
│       ├── datamarts.py
│       └── ddl.py
├── sql/
│   ├── init_postgres.sql
│   └── ddl/
│       ├── webinar_4_tables.sql
│       ├── final_staging_tables.sql
│       ├── final_dwh_tables.sql
│       └── final_datamarts.sql
├── data/
│   ├── sample/
│   │   ├── sample_nested.json
│   │   ├── sample_nested.xml
│   │   └── sample_temperature.csv
│   └── processed/
│       ├── webinar_2/
│       └── webinar_3/
└── tests/
    ├── test_webinar_2.py
    ├── test_webinar_3.py
    ├── test_webinar_4.py
    └── test_final_project.py
```

## Настройка источников через переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `JSON_SOURCE_PATH` | Путь к JSON-файлу | sample fallback |
| `JSON_SOURCE_URL` | URL для скачивания JSON | — |
| `XML_SOURCE_PATH` | Путь к XML-файлу | sample fallback |
| `XML_SOURCE_URL` | URL для скачивания XML | — |
| `DATASET_PATH` | Путь к CSV с температурами | sample fallback |
| `DATASET_URL` | URL для скачивания CSV | — |
| `INCREMENTAL_DAYS` | Глубина инкрементальной загрузки | 3 |

## Тесты

```bash
pip install pytest pandas lxml psycopg2-binary pymongo sqlalchemy pydantic requests
cd etl_module_3_project
PYTHONPATH=src python -m pytest tests/ -v
```

## Технологический стек

- Python 3.11
- Apache Airflow 2.8.1
- PostgreSQL 15
- MongoDB 7
- Docker Compose
- pandas, SQLAlchemy, psycopg2, pymongo, lxml, pydantic
