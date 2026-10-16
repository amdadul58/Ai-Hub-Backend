from src.vector_db.client import get_vector_store

def get_collection(name="default"):
    safe_name = "".join(c for c in name if c.isalnum() or c in "-_")
    if not safe_name:
        raise ValueError("Collection name cannot be empty")
    return get_vector_store(f"data/vector_db/{safe_name}.json")
