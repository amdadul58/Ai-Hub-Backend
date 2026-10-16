from src.database.session import database_connection


class UserRepository:
    def create(self, username, email=None, password_hash=None):
        if not username or not username.strip():
            raise ValueError("username cannot be empty.")

        with database_connection() as db:
            row = db.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (username.strip(), email, password_hash),
            ).fetchone()
            return dict(row)

    def get(self, user_id):
        with database_connection() as db:
            row = db.execute(
                "SELECT * FROM users WHERE id = %s",
                (int(user_id),),
            ).fetchone()
            return dict(row) if row else None

    def list(self, limit=100):
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500.")

        with database_connection() as db:
            rows = db.execute(
                """
                SELECT id, username, email, is_active, created_at
                FROM users ORDER BY id DESC LIMIT %s
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def set_active(self, user_id, active):
        with database_connection() as db:
            cursor = db.execute(
                "UPDATE users SET is_active = %s WHERE id = %s",
                (int(bool(active)), int(user_id)),
            )
            return cursor.rowcount > 0
