import json
from src.database.session import database_connection


class ModelRepository:
    def register(self, model_name, version, artifact_path, stage="staging", metrics=None):
        if stage not in {"staging", "production", "archived"}:
            raise ValueError("Invalid model stage.")

        with database_connection() as db:
            row = db.execute(
                """
                INSERT INTO model_versions
                    (model_name, version, artifact_path, stage, metrics_json)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (model_name, version, artifact_path, stage, json.dumps(metrics or {})),
            ).fetchone()
            return dict(row)

    def list_versions(self, model_name=None):
        with database_connection() as db:
            if model_name:
                rows = db.execute(
                    "SELECT * FROM model_versions WHERE model_name = %s ORDER BY id DESC",
                    (model_name,),
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM model_versions ORDER BY id DESC"
                ).fetchall()

            result = []
            for row in rows:
                item = dict(row)
                item["metrics"] = json.loads(item.pop("metrics_json"))
                result.append(item)
            return result
