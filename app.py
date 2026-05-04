from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "dacha_booking.sqlite3"))


FLOORS = [
    {
        "id": "house-1",
        "building": "house",
        "buildingName": "Дом",
        "floor": 1,
        "title": "Дом, этаж 1",
        "subtitle": "Главная комната и кровать поближе к кухне",
        "canvas": {"width": 1180, "height": 520},
        "rooms": [
            {"x": 4, "y": 6, "w": 60, "h": 66, "label": "Большая комната"},
            {"x": 64, "y": 6, "w": 16, "h": 66, "label": "Кухня"},
            {"x": 80, "y": 6, "w": 20, "h": 66, "label": "Правая комната"},
            {"x": 4, "y": 72, "w": 76, "h": 22, "label": "Нижний коридор"},
        ],
        "walls": [
            {"x": 4, "y": 6, "w": 96, "h": 1.15},
            {"x": 4, "y": 6, "w": 1.15, "h": 88},
            {"x": 99, "y": 6, "w": 1.15, "h": 66},
            {"x": 4, "y": 71, "w": 76, "h": 1.15},
            {"x": 80, "y": 71, "w": 20, "h": 1.15},
            {"x": 4, "y": 93, "w": 76, "h": 1.15},
            {"x": 79.4, "y": 6, "w": 1.15, "h": 88},
            {"x": 63.4, "y": 6, "w": 1.15, "h": 66},
        ],
        "beds": [
            {"id": "house-1-1", "label": "Дом 1.1", "note": "Диван для двоих, но может третий поместиться", "x": 8, "y": 13, "w": 4.8, "h": 35, "orientation": "vertical"},
            {"id": "house-1-2", "label": "Дом 1.2", "note": "Диван для двоих, но может третий поместиться", "x": 14.2, "y": 13, "w": 4.8, "h": 35, "orientation": "vertical"},
            {"id": "house-1-3", "label": "Дом 1.3", "note": "Диван для двоих, но может третий поместиться", "x": 20.4, "y": 13, "w": 4.8, "h": 35, "orientation": "vertical"},
            {"id": "house-1-4", "label": "Дом 1.4", "note": "Кресло раскладное", "x": 29.2, "y": 38, "w": 4.8, "h": 30, "orientation": "vertical"},
            {"id": "house-1-5", "label": "Дом 1.5", "note": "Оранжевая кровать в кухне", "x": 84, "y": 55, "w": 14, "h": 12, "orientation": "horizontal"},
        ],
    },
    {
        "id": "house-2",
        "building": "house",
        "buildingName": "Дом",
        "floor": 2,
        "title": "Дом, этаж 2",
        "subtitle": "Три зоны сна",
        "canvas": {"width": 780, "height": 540},
        "rooms": [
            {"x": 2, "y": 3, "w": 28, "h": 52, "label": "Левая комната"},
            {"x": 2, "y": 55, "w": 28, "h": 40, "label": "Нижняя комната"},
            {"x": 30, "y": 3, "w": 44, "h": 92, "label": "Средняя комната"},
            {"x": 74, "y": 3, "w": 24, "h": 92, "label": "Правая комната"},
        ],
        "walls": [
            {"x": 2, "y": 3, "w": 96, "h": 1.15},
            {"x": 2, "y": 3, "w": 1.15, "h": 92},
            {"x": 97, "y": 3, "w": 1.15, "h": 92},
            {"x": 2, "y": 94, "w": 96, "h": 1.15},
            {"x": 29.4, "y": 3, "w": 1.15, "h": 92},
            {"x": 2, "y": 54.4, "w": 28, "h": 1.15},
            {"x": 73.4, "y": 3, "w": 1.15, "h": 92},
        ],
        "beds": [
            {"id": "house-2-1", "label": "Дом 2.1", "note": "Барская", "x": 6, "y": 15, "w": 6.8, "h": 30, "orientation": "vertical"},
            {"id": "house-2-2", "label": "Дом 2.2", "note": "Барская", "x": 17, "y": 15, "w": 6.8, "h": 30, "orientation": "vertical"},
            {"id": "house-2-3", "label": "Дом 2.3", "note": "Приближенные помещика", "x": 34, "y": 12, "w": 6.8, "h": 34, "orientation": "vertical"},
            {"id": "house-2-4", "label": "Дом 2.4", "note": "Приближенные помещика", "x": 45, "y": 12, "w": 6.8, "h": 34, "orientation": "vertical"},
            {"id": "house-2-5", "label": "Дом 2.5", "note": "Раскладушка (удобная) - можно переставить", "x": 60, "y": 15, "w": 5.2, "h": 25, "orientation": "vertical"},
            {"id": "house-2-6", "label": "Дом 2.6", "note": "Тахта для двоих (традиционное место Павла Жука)", "x": 78, "y": 10, "w": 18, "h": 11, "orientation": "horizontal"},
            {"id": "house-2-7", "label": "Дом 2.7", "note": "Этой комнаты боялись даже чеченцы", "x": 7, "y": 64, "w": 18, "h": 10, "orientation": "horizontal"},
            {"id": "house-2-8", "label": "Дом 2.8", "note": "Этой комнаты боялись даже чеченцы", "x": 7, "y": 80, "w": 18, "h": 10, "orientation": "horizontal"},
            {"id": "house-2-9", "label": "Дом 2.9", "note": "Тахта для двоих (традиционное место Павла Жука)", "x": 78, "y": 26, "w": 18, "h": 11, "orientation": "horizontal"},
        ],
    },
    {
        "id": "house-3",
        "building": "house",
        "buildingName": "Дом",
        "floor": 3,
        "title": "Дом, этаж 3",
        "subtitle": "Мансардная дипломатия: две вертикальные кровати наверху и две лежанки внизу. (че это значит)",
        "canvas": {"width": 760, "height": 700},
        "rooms": [
            {"x": 28, "y": 2, "w": 44, "h": 52, "label": "Верхняя зона"},
            {"x": 8, "y": 54, "w": 84, "h": 42, "label": "Нижняя зона"},
        ],
        "walls": [
            {"x": 28, "y": 2, "w": 44, "h": 1.15},
            {"x": 28, "y": 2, "w": 1.15, "h": 52},
            {"x": 71, "y": 2, "w": 1.15, "h": 52},
            {"x": 28, "y": 53, "w": 44, "h": 1.15},
            {"x": 8, "y": 54, "w": 84, "h": 1.15},
            {"x": 8, "y": 54, "w": 1.15, "h": 42},
            {"x": 91, "y": 54, "w": 1.15, "h": 42},
            {"x": 8, "y": 95, "w": 84, "h": 1.15},
        ],
        "beds": [
            {"id": "house-3-1", "label": "Дом 3.1", "note": "Кровать для двоих", "x": 54, "y": 17, "w": 6.8, "h": 29, "orientation": "vertical"},
            {"id": "house-3-2", "label": "Дом 3.2", "note": "Кровать для двоих", "x": 64, "y": 17, "w": 6.8, "h": 29, "orientation": "vertical"},
            {"id": "house-3-3", "label": "Дом 3.3", "note": "Матрац", "x": 63, "y": 70, "w": 19, "h": 10, "orientation": "horizontal"},
            {"id": "house-3-4", "label": "Дом 3.4", "note": "Матрац", "x": 63, "y": 83, "w": 19, "h": 10, "orientation": "horizontal"},
        ],
    },
    {
        "id": "sauna-1",
        "building": "sauna",
        "buildingName": "Баня",
        "floor": 1,
        "title": "Баня, этаж 1",
        "subtitle": "Две комнаты, две кровати",
        "canvas": {"width": 980, "height": 390},
        "rooms": [
            {"x": 3, "y": 7, "w": 47, "h": 86, "label": "Левая комната"},
            {"x": 50, "y": 7, "w": 47, "h": 86, "label": "Правая комната"},
        ],
        "walls": [
            {"x": 3, "y": 7, "w": 94, "h": 1.15},
            {"x": 3, "y": 7, "w": 1.15, "h": 86},
            {"x": 96, "y": 7, "w": 1.15, "h": 86},
            {"x": 3, "y": 92, "w": 94, "h": 1.15},
            {"x": 49.4, "y": 7, "w": 1.15, "h": 86},
        ],
        "beds": [
            {"id": "sauna-1-1", "label": "Баня 1.1", "note": "Здесь никто никогда не спал и не советую", "x": 13, "y": 17, "w": 20, "h": 13, "orientation": "horizontal"},
            {"id": "sauna-1-2", "label": "Баня 1.2", "note": "Прямиком в сауне на досках", "x": 71, "y": 17, "w": 20, "h": 13, "orientation": "horizontal"},
        ],
    },
    {
        "id": "sauna-2",
        "building": "sauna",
        "buildingName": "Баня",
        "floor": 2,
        "title": "Баня, этаж 2",
        "subtitle": "Четыре места для тех, кто поднялся выше уровня бытовых споров.",
        "canvas": {"width": 1040, "height": 430},
        "rooms": [
            {"x": 3, "y": 7, "w": 47, "h": 86, "label": "Левая комната"},
            {"x": 50, "y": 7, "w": 47, "h": 86, "label": "Правая комната"},
        ],
        "walls": [
            {"x": 3, "y": 7, "w": 94, "h": 1.15},
            {"x": 3, "y": 7, "w": 1.15, "h": 86},
            {"x": 96, "y": 7, "w": 1.15, "h": 86},
            {"x": 3, "y": 92, "w": 94, "h": 1.15},
            {"x": 49.4, "y": 7, "w": 1.15, "h": 86},
        ],
        "beds": [
            {"id": "sauna-2-1", "label": "Баня 2.1", "note": "Кайфовый матрас для двоих", "x": 22, "y": 30, "w": 5.4, "h": 43, "orientation": "vertical"},
            {"id": "sauna-2-2", "label": "Баня 2.2", "note": "Кайфовый матрас для двоих", "x": 31, "y": 30, "w": 5.4, "h": 43, "orientation": "vertical"},
            {"id": "sauna-2-3", "label": "Баня 2.3", "note": "Диван для двоих", "x": 82, "y": 30, "w": 5.4, "h": 43, "orientation": "vertical"},
            {"id": "sauna-2-4", "label": "Баня 2.4", "note": "Диван для двоих", "x": 91, "y": 30, "w": 5.4, "h": 43, "orientation": "vertical"},
        ],
    },
]

BED_IDS = {bed["id"] for floor in FLOORS for bed in floor["beds"]}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False

    @app.before_request
    def ensure_database() -> None:
        init_db()

    @app.teardown_appcontext
    def close_connection(exception: BaseException | None) -> None:
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    @app.get("/")
    def index():
        return render_template("index.html", floors=FLOORS)

    @app.get("/api/floors")
    def get_floors():
        return jsonify({"floors": FLOORS})

    @app.get("/api/bookings")
    def get_bookings():
        rows = query_bookings()
        return jsonify({"bookings": [dict(row) for row in rows]})

    @app.post("/api/bookings")
    def create_booking():
        payload = request.get_json(silent=True) or {}
        bed_id = str(payload.get("bed_id", "")).strip()
        name = str(payload.get("name", "")).strip()
        contact = str(payload.get("contact", "")).strip()
        comment = str(payload.get("comment", "")).strip()

        if bed_id not in BED_IDS:
            return jsonify({"error": "Такого спального места нет на плане."}), 400
        if len(name) < 2:
            return jsonify({"error": "Введите имя хотя бы из двух букв."}), 400
        if len(name) > 80 or len(contact) > 120 or len(comment) > 300:
            return jsonify({"error": "Слишком длинные данные для дачной летописи."}), 400

        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            db = get_db()
            db.execute(
                """
                INSERT INTO bookings (bed_id, name, contact, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (bed_id, name, contact, comment, created_at),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "Это место уже занято."}), 409

        booking = dict(get_booking(bed_id))
        return jsonify({"booking": booking, "message": "Место забронировано."}), 201

    @app.delete("/api/bookings/<bed_id>")
    def delete_booking(bed_id: str):
        if bed_id not in BED_IDS:
            return jsonify({"error": "Такого спального места нет на плане."}), 400

        db = get_db()
        cursor = db.execute("DELETE FROM bookings WHERE bed_id = ?", (bed_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "На этом месте сейчас никто не числится."}), 404

        return jsonify({"message": "Выписка оформлена. Место снова свободно."})

    return app


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        DATABASE.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(DATABASE)
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bed_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            contact TEXT DEFAULT '',
            comment TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )
    db.commit()


def query_bookings() -> list[sqlite3.Row]:
    return get_db().execute(
        """
        SELECT id, bed_id, name, contact, comment, created_at
        FROM bookings
        ORDER BY created_at DESC
        """
    ).fetchall()


def get_booking(bed_id: str) -> sqlite3.Row:
    return get_db().execute(
        """
        SELECT id, bed_id, name, contact, comment, created_at
        FROM bookings
        WHERE bed_id = ?
        """,
        (bed_id,),
    ).fetchone()


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
