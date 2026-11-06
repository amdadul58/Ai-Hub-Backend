def route_task(task):
    text = str(task or "").strip().lower()

    if not text:
        return "general_response"

    # Route explicit questions to document search, including Bengali questions.
    if text.endswith("?") or text.endswith("\u0964"):
        return "search_documents"

    summary_terms = (
        "summarize", "summary", "summarise", "summarisation",
        "\u09b8\u09be\u09b0\u09be\u0982\u09b6",
        "\u09b8\u09be\u09b0\u09b8\u0982\u0995\u09cd\u09b7\u09c7\u09aa",
        "\u09b8\u0982\u0995\u09cd\u09b7\u09c7\u09aa\u09c7",
        "\u09b8\u0982\u0995\u09cd\u09b7\u09bf\u09aa\u09cd\u09a4\u09b8\u09be\u09b0",
    )
    if any(term in text for term in summary_terms):
        return "summarize_text"

    search_terms = (
        "search", "find", "look up", "knowledge base", "document",
        "documents", "pdf", "rag", "answer", "question", "what is",
        "who is", "where is", "when is", "why", "how", "explain",
        "tell me about",
        "\u09a4\u09a5\u09cd\u09af",
        "\u0996\u09c1\u0981\u099c\u09c7",
        "\u0996\u09c1\u0981\u099c\u09c1\u09a8",
        "\u0985\u09a8\u09c1\u09b8\u09a8\u09cd\u09a7\u09be\u09a8",
        "\u0989\u09a4\u09cd\u09a4\u09b0",
        "\u09aa\u09cd\u09b0\u09b6\u09cd\u09a8",
        "\u09ac\u09cd\u09af\u09be\u0996\u09cd\u09af\u09be",
        "\u0995\u09c0", "\u0995\u09bf", "\u0995\u09c7",
        "\u0995\u09cb\u09a5\u09be\u09af\u09bc",
        "\u0995\u09c7\u09a8", "\u0995\u09bf\u09ad\u09be\u09ac\u09c7",
        "\u09b8\u09ae\u09cd\u09aa\u09b0\u09cd\u0995\u09c7 \u09ac\u09b2\u09c1\u09a8",
    )
    if any(term in text for term in search_terms):
        return "search_documents"

    return "general_response"
