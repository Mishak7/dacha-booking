# Для выезда на дачу в Шапки)

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Деплой
- build command: `pip install -r requirements.txt`
- start command: `gunicorn app:app`
- переменная `DATABASE_PATH` опциональна; без нее база создается рядом с приложением.
