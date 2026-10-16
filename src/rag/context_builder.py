def build_context(results, max_chars=5000):
    parts = []
    used = 0
    for item in results:
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        source = item.get("metadata", {}).get("source", "unknown")
        block = f"[Source: {source}]\n{text}"
        remaining = max_chars - used
        if remaining <= 0:
            break
        block = block[:remaining]
        parts.append(block)
        used += len(block)
    return "\n\n".join(parts)
