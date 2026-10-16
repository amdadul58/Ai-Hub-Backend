import os
from pathlib import Path

def load_local_model(model_path, **kwargs):
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Local model path not found: {path}")
    tokenizer = AutoTokenizer.from_pretrained(str(path), local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        str(path), local_files_only=True, **kwargs
    )
    model.eval()
    return tokenizer, model
