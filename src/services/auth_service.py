import psycopg

from src.core.security import hash_password, verify_password, create_access_token
from src.database.repositories.user_repository import UserRepository
from src.database.session import database_connection


class AuthService:
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def register(self, username, password, email=None):
        password_hash = hash_password(password)
        try:
            user = self.repository.create(username, email, password_hash)
        except psycopg.IntegrityError as exc:
            raise ValueError("Username or email is already registered.") from exc

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        }

    def login(self, username, password):
        with database_connection() as db:
            row = db.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,),
            ).fetchone()

        if not row or not row["is_active"] or not row["password_hash"]:
            raise ValueError("Invalid username or password.")

        if not verify_password(password, row["password_hash"]):
            raise ValueError("Invalid username or password.")

        token = create_access_token(str(row["id"]))
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": row["id"], "username": row["username"]},
        }
