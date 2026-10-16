def make_citations(results):
    citations = []
    for i, item in enumerate(results, start=1):
        metadata = item.get("metadata", {})
        citations.append({
            "id": i,
            "source": metadata.get("source", "unknown"),
            "chunk": metadata.get("chunk"),
            "score": item.get("score", 0),
        })
    return citations
