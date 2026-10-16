from src.database.session import database_connection


def get_dashboard_summary():
    tables = (
        "users", "conversations", "messages", "documents",
        "model_versions", "training_jobs", "inference_logs",
        "traffic_events", "audit_logs",
    )

    with database_connection() as db:
        counts = {}
        for table in tables:
            counts[table] = db.execute(
                f'SELECT COUNT(*) AS total FROM "{table}"'
            ).fetchone()["total"]

    return {"status": "ok", "database": "postgresql", "counts": counts}
