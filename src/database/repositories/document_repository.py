from src.database.session import database_connection


class DocumentRepository:
    def create(self, filename, file_path, content_type=None, status="uploaded"):
        if not filename or not file_path:
            raise ValueError("filename and file_path are required.")

        with database_connection() as db:
            row = db.execute(
                """
                INSERT INTO documents (filename, file_path, content_type, status)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """,
                (filename, file_path, content_type, status),
            ).fetchone()
            return dict(row)

    def get(self, document_id):
        with database_connection() as db:
            row = db.execute(
                "SELECT * FROM documents WHERE id = %s",
                (int(document_id),),
            ).fetchone()
            return dict(row) if row else None
