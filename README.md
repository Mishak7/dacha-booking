# Дачный сонный штаб

Шуточный сервис бронирования спальных мест на даче. Внутри есть интерактивные схемы дома и бани, форма бронирования и SQLite-база.

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

После запуска откройте `http://127.0.0.1:5000`.

## Деплой

Проект готов для Render, Railway, Fly.io или любого хостинга с Python:

- build command: `pip install -r requirements.txt`
- start command: `gunicorn app:app`
- переменная `DATABASE_PATH` опциональна; без нее база создается рядом с приложением.

Для продакшена лучше подключить постоянный диск или заменить SQLite на Postgres, чтобы брони не пропадали при пересоздании контейнера.
