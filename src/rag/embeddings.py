import hashlib
import math
import re

def embed_text(text, dimensions=256):
    if dimensions < 16:
        raise ValueError("dimensions must be at least 16")
    vector = [0.0] * dimensions
    tokens = re.findall(r"\w+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0
    norm = math.sqrt(sum(x * x for x in vector))
    if norm:
        vector = [x / norm for x in vector]
    return vector

def embed_texts(texts, dimensions=256):
    return [embed_text(text, dimensions) for text in texts]
