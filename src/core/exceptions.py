class AIHubError(Exception):
    """Base exception for AI Hub."""

class ModelUnavailableError(AIHubError):
    """A required local AI model is unavailable."""

class DocumentProcessingError(AIHubError):
    """Document processing failed."""

class RetrievalError(AIHubError):
    """Document retrieval failed."""
