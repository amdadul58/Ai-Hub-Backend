from src.database.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def get_user(self, user_id):
        user = self.repository.get(user_id)
        if user:
            user.pop("password_hash", None)
        return user

    def list_users(self, limit=100):
        return self.repository.list(limit)

    def set_active(self, user_id, active):
        return self.repository.set_active(user_id, bool(active))
