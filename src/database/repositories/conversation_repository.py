from src.database.session import database_connection


class ConversationRepository:
    def create(self, title="New conversation", user_id=None):
        user_id = int(user_id) if user_id is not None else None

        with database_connection() as db:
            row = db.execute(
                """
                INSERT INTO conversations (title, user_id)
                VALUES (%s, %s)
                RETURNING *
                """,
                (title, user_id),
            ).fetchone()
            return dict(row)

    def add_message(self, conversation_id, role, content):
        if role not in {"system", "user", "assistant", "tool"}:
            raise ValueError("Unsupported message role.")

        with database_connection() as db:
            row = db.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (int(conversation_id), role, content),
            ).fetchone()

            db.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP::text WHERE id = %s",
                (int(conversation_id),),
            )
            return dict(row)

    def get_messages(self, conversation_id, limit=200):
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")

        with database_connection() as db:
            rows = db.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = %s
                ORDER BY id LIMIT %s
                """,
                (int(conversation_id), limit),
            ).fetchall()
            return [dict(row) for row in rows]
