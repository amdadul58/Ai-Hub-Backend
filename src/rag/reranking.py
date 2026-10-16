def rerank_results(results, query=None, top_k=5):
    ranked = sorted(
        results,
        key=lambda item: item.get("score", 0),
        reverse=True,
    )
    return ranked[:max(0, top_k)]
