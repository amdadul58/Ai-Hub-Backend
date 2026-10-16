def route_task(task):
    text = str(task).lower()
    if any(word in text for word in ("document", "pdf", "knowledge base", "search")):
        return "search_documents"
    if any(word in text for word in ("summarize", "summary")):
        return "summarize_text"
    return "general_response"
