def combine_evidence(question, evidence, answer_builder=None):
    """Combine text evidence; an optional callback can produce a final answer."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question cannot be empty.")
    normalized = []
    for item in evidence:
        if isinstance(item, str):
            normalized.append({"source": "unspecified", "content": item})
        elif isinstance(item, dict) and "content" in item:
            normalized.append({
                "source": str(item.get("source", "unspecified")),
                "content": str(item["content"]),
            })
        else:
            raise ValueError("Each evidence item must be text or a dict with content.")
    if answer_builder is not None:
        if not callable(answer_builder):
            raise TypeError("answer_builder must be callable.")
        answer = answer_builder(question.strip(), normalized)
    else:
        answer = "\n".join(item["content"] for item in normalized)
    return {
        "question": question.strip(),
        "evidence": normalized,
        "answer": answer,
        "evidence_count": len(normalized),
    }
