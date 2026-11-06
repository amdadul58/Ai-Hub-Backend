import os
import re
import uuid

from google.auth.transport.requests import Request
from google.oauth2 import id_token as google_id_token

from src.core.security import create_access_token
from src.database.session import database_connection


class GoogleAuthService:
    def login(self, token: str):
        client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        admin_email = os.getenv(
            "GOOGLE_ALLOWED_ADMIN_EMAIL",
            "amdadul2458@gmail.com",
        ).strip().lower()

        if not client_id:
            raise RuntimeError(
                "Google OAuth client is not configured. "
                "Set GOOGLE_CLIENT_ID in the backend .env file."
            )

        if not token or not token.strip():
            raise ValueError("Google did not provide an ID token.")

        # Verify the token with Google. Never trust the email supplied
        # by the frontend without verifying Google's signed ID token.
        try:
            claims = google_id_token.verify_oauth2_token(
                token.strip(),
                Request(),
                audience=client_id,
            )
        except ValueError as exc:
            reason = str(exc).strip() or "Token validation failed."
            raise ValueError(
                f"Google rejected the ID token: {reason} "
                "Check that the frontend and backend use the same "
                "Google OAuth client ID and that the sign-in token is fresh."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "Could not verify the Google ID token. "
                "Check backend internet access and Google OAuth configuration. "
                f"Verification error: {type(exc).__name__}: {exc}"
            ) from exc

        email = str(claims.get("email", "")).strip().lower()
        email_verified = claims.get("email_verified") is True

        if not email or not email_verified:
            raise ValueError("A verified Google email is required.")

        role = "admin" if email == admin_email else "user"

        with database_connection() as db:
            user = db.execute(
                """
                SELECT id, username, email, is_active
                FROM users
                WHERE LOWER(TRIM(email)) = %s
                """,
                (email,),
            ).fetchone()

            if user:
                if not user["is_active"]:
                    raise ValueError(
                        "This AI Hub account is inactive. Contact an administrator."
                    )

                db.execute(
                    "UPDATE users SET role = %s WHERE id = %s",
                    (role, user["id"]),
                )
                user_id = user["id"]
                username = user["username"]

            else:
                # Generate a readable, unique username for first-time users.
                base = email.split("@", 1)[0].lower()
                base = re.sub(r"[^a-z0-9_.-]", "_", base).strip("._-")
                base = (base or "google_user")[:40]
                username = base

                existing = db.execute(
                    "SELECT 1 FROM users WHERE username = %s",
                    (username,),
                ).fetchone()

                if existing:
                    username = f"{base[:30]}_{uuid.uuid4().hex[:8]}"

                created = db.execute(
                    """
                    INSERT INTO users (username, email, role)
                    VALUES (%s, %s, %s)
                    RETURNING id, username
                    """,
                    (username, email, role),
                ).fetchone()

                user_id = created["id"]
                username = created["username"]

        access_token = create_access_token(str(user_id))

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "role": role,
            },
        }
