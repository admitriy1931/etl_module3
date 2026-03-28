# Инструкция по запуску и демонстрации проекта

## Шаг 1. Подготовка

```bash
cd etl_module_3_project

# Убедись что нет старых контейнеров/томов
docker-compose down -v

# Запусти всё
docker-compose up -d
```

Подожди 1–2 минуты. Проверь что всё поднялось:

```bash
docker-compose ps
```

Все сервисы должны быть `running` (кроме `airflow-init` — он `exited (0)`).

Если `airflow-init` упал — смотри логи:
```bash
docker-compose logs airflow-init
```

---

## Шаг 2. Открой Airflow UI

Браузер → http://localhost:8080
Логин: `admin` / Пароль: `admin`

Ты увидишь 6 DAG-ов. Все выключены по умолчанию.

---

## Шаг 3. Запусти DAG-и в правильном порядке

### 3.1 — Webinar 2 (flatten JSON/XML)
1. Включи тумблер у `webinar_2_flatten_sources_dag`
2. Нажми кнопку ▶ (Trigger DAG)
3. Дождись зелёного статуса (success)
4. **Сделай скриншот** — DAG Graph или Grid View с зелёными задачами

### 3.2 — Webinar 3 (transform weather)
1. Включи и запусти `webinar_3_transform_weather_dag`
2. Дождись success
3. **Скриншот**

### 3.3 — Webinar 4 (load to PostgreSQL)
1. Включи и запусти `webinar_4_load_to_postgres_dag`
2. Дождись success (оба таска: `full_historical_load` → `incremental_load`)
3. **Скриншот**

### 3.4 — Final: генерация данных MongoDB
1. Включи и запусти `final_generate_mongo_data_dag`
2. Дождись success
3. **Скриншот**

### 3.5 — Final: репликация MongoDB → PostgreSQL
1. Включи и запусти `final_replicate_mongo_to_postgres_dag`
2. Дождись success (7 тасков: create_tables → 5 параллельных load → promote_to_dwh)
3. **Скриншот**

### 3.6 — Final: витрины
1. Включи и запусти `final_build_datamarts_dag`
2. Дождись success
3. **Скриншот**

---

## Шаг 4. Проверь результаты в терминале

### 4.1 — Проверь файлы Webinar 2

```bash
ls -la data/processed/webinar_2/
```

Должны быть:
- `json_employees.csv`
- `json_employee_skills.csv`
- `json_employee_projects.csv`
- `json_offices.csv`
- `xml_books.csv`
- `xml_book_tags.csv`
- `xml_book_reviews.csv`

Можно показать содержимое:
```bash
head -5 data/processed/webinar_2/json_employees.csv
head -5 data/processed/webinar_2/xml_books.csv
```

### 4.2 — Проверь файлы Webinar 3

```bash
ls -la data/processed/webinar_3/
```

Должны быть:
- `cleaned_weather.csv`
- `hottest_5_days.csv`
- `coldest_5_days.csv`

```bash
cat data/processed/webinar_3/hottest_5_days.csv
cat data/processed/webinar_3/coldest_5_days.csv
```

### 4.3 — Проверь PostgreSQL (Webinar 4 + Final)

```bash
# Узнай имя контейнера postgres
docker-compose ps

# Подключись (имя контейнера может отличаться)
docker exec -it etl_module_3_project-postgres-1 psql -U etl_user -d etl_project
```

Внутри psql:

```sql
-- Webinar 4: weather data
SELECT COUNT(*) FROM dwh.weather;
SELECT * FROM dwh.weather ORDER BY noted_date LIMIT 5;
SELECT * FROM staging.load_state;

-- Final: sessions
SELECT COUNT(*) FROM dwh.sessions;
SELECT COUNT(*) FROM dwh.session_pages;
SELECT COUNT(*) FROM dwh.session_actions;

-- Final: events
SELECT COUNT(*) FROM dwh.events;

-- Final: tickets
SELECT COUNT(*) FROM dwh.tickets;
SELECT COUNT(*) FROM dwh.ticket_messages;

-- Final: recommendations
SELECT COUNT(*) FROM dwh.recommendations;
SELECT COUNT(*) FROM dwh.recommendation_products;

-- Final: moderation
SELECT COUNT(*) FROM dwh.moderation_reviews;
SELECT COUNT(*) FROM dwh.moderation_flags;

-- Витрина 1: активность пользователей
SELECT * FROM mart.dm_user_activity LIMIT 10;

-- Витрина 2: эффективность поддержки
SELECT * FROM mart.dm_support_efficiency LIMIT 10;

-- Выход
\q
```

### 4.4 — Проверь MongoDB

```bash
docker exec -it etl_module_3_project-mongodb-1 mongosh etl_source --eval "
  print('user_sessions:', db.user_sessions.countDocuments());
  print('event_logs:', db.event_logs.countDocuments());
  print('support_tickets:', db.support_tickets.countDocuments());
  print('user_recommendations:', db.user_recommendations.countDocuments());
  print('moderation_queue:', db.moderation_queue.countDocuments());
"
```

Ожидаемый вывод:
```
user_sessions: 1000
event_logs: 5000
support_tickets: 500
user_recommendations: 200
moderation_queue: 800
```

---

## Шаг 5. Загрузи на GitHub

```bash
cd etl_module_3_project

git init
git add .
git commit -m "ETL Module 3 — unified data platform project"

# Создай репозиторий на GitHub, затем:
git remote add origin https://github.com/<username>/<repo-name>.git
git branch -M main
git push -u origin main
```

---

## Шаг 6. Что прикрепить в LMS

### Для Вебинара 2:
- Ссылка на GitHub
- Скриншот: `webinar_2_flatten_sources_dag` — Graph View, все таски зелёные

### Для Вебинара 3:
- Ссылка на GitHub
- Скриншот: `webinar_3_transform_weather_dag` — все таски зелёные

### Для Вебинара 4:
- Ссылка на GitHub
- Скриншот: `webinar_4_load_to_postgres_dag` — оба таска зелёные

### Для итогового задания:
- Ссылка на GitHub
- Скриншоты:
  1. `final_generate_mongo_data_dag` — success
  2. `final_replicate_mongo_to_postgres_dag` — success (видно 7 тасков)
  3. `final_build_datamarts_dag` — success
  4. (Бонус) Скриншот запроса к витрине в psql

---

## Возможные проблемы

### DAG не появился в Airflow
```bash
docker-compose logs airflow-scheduler | tail -30
```
Обычно проблема с импортами. Проверь что `PYTHONPATH=/opt/airflow/src` задан.

### PostgreSQL: "relation does not exist"
Убедись что `init_postgres.sql` сработал. Проверь:
```bash
docker exec -it etl_module_3_project-postgres-1 psql -U etl_user -d etl_project -c "\dn"
```
Должны быть схемы: `staging`, `dwh`, `mart`.

Если схем нет — пересоздай всё:
```bash
docker-compose down -v
docker-compose up -d
```

### MongoDB connection refused
Подожди 10–15 секунд после `docker-compose up`, MongoDB стартует не мгновенно.
