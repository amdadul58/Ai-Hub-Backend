def route_task(task):
    text = str(task).strip().lower()

    if any(word in text for word in ("summarize", "summary", "সারাংশ")):
        return "summarize_text"

    if any(word in text for word in (
        "document",
        "pdf",
        "knowledge base",
        "search",
        "rag",
        "answer",
        "question",
        "what is",
        "who is",
        "explain",
        "find",
        "খুঁজে",
        "উত্তর",
    )):
        return "search_documents"

    return "general_response"
