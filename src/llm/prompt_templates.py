DEFAULT_SYSTEM_PROMPT = (
    "You are AI Hub, a helpful assistant. "
    "Be accurate, clear, and admit uncertainty when needed."
)

RAG_PROMPT_TEMPLATE = """Answer using the context below when relevant.
If the context does not contain the answer, say so clearly.

Context:
{context}

Question:
{question}

Answer:"""
