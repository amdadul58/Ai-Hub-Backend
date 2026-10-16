from src.database.repositories.conversation_repository import ConversationRepository


class HistoryService:
    def __init__(self, repository=None):
        self.repository = repository or ConversationRepository()

    def create_conversation(self, title="New conversation", user_id=None):
        return self.repository.create(title, user_id)

    def add_message(self, conversation_id, role, content):
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Message content cannot be empty.")
        return self.repository.add_message(conversation_id, role, content)

    def get_messages(self, conversation_id, limit=200):
        return self.repository.get_messages(conversation_id, limit)
