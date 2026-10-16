import json
from src.database.session import database_connection


class TrafficRepository:
    def create(self, event_type, location=None, details=None):
        with database_connection() as db:
            row = db.execute(
                """
                INSERT INTO traffic_events (event_type, location, details_json)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (event_type, location, json.dumps(details or {})),
            ).fetchone()
            return dict(row)

    def list_recent(self, limit=100):
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")

        with database_connection() as db:
            rows = db.execute(
                "SELECT * FROM traffic_events ORDER BY id DESC LIMIT %s",
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]
