
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

    return {
        "status": "ok",
        "database": "postgresql",
        "counts": counts,
    }


def get_usage_analytics(days: int = 7):
    if days not in (7, 30, 90):
        raise ValueError("days must be 7, 30, or 90")

    with database_connection() as db:
        daily_rows = db.execute(
            """
            SELECT
                created_at::timestamptz::date::text AS date,
                COUNT(*) AS total,
                COUNT(*) FILTER (
                    WHERE LOWER(status) IN ('success', 'succeeded', 'completed')
                ) AS successful,
                COUNT(*) FILTER (
                    WHERE LOWER(status) NOT IN ('success', 'succeeded', 'completed')
                ) AS unsuccessful,
                ROUND(AVG(latency_ms)::numeric, 2) AS avg_latency_ms
            FROM inference_logs
            WHERE created_at::timestamptz >= NOW() - (%s * INTERVAL '1 day')
              AND created_at::timestamptz <= NOW()
            GROUP BY created_at::timestamptz::date
            ORDER BY created_at::timestamptz::date
            """,
            (days,),
        ).fetchall()

        model_rows = db.execute(
            """
            SELECT model_name, COUNT(*) AS total
            FROM inference_logs
            WHERE created_at::timestamptz >= NOW() - (%s * INTERVAL '1 day')
              AND created_at::timestamptz <= NOW()
            GROUP BY model_name
            ORDER BY total DESC
            """,
            (days,),
        ).fetchall()

    return {
        "status": "ok",
        "period_days": days,
        "total_requests": sum(row["total"] for row in daily_rows),
        "daily": [
            {
                "date": row["date"],
                "total": row["total"],
                "successful": row["successful"],
                "unsuccessful": row["unsuccessful"],
                "avg_latency_ms": (
                    float(row["avg_latency_ms"])
                    if row["avg_latency_ms"] is not None
                    else None
                ),
            }
            for row in daily_rows
        ],
        "models": [
            {"model_name": row["model_name"], "total": row["total"]}
            for row in model_rows
        ],
    }

