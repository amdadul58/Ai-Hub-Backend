def filter_metadata(results, filters=None):
    if not filters:
        return list(results)
    output = []
    for item in results:
        metadata = item.get("metadata", {})
        if all(metadata.get(key) == value for key, value in filters.items()):
            output.append(item)
    return output
