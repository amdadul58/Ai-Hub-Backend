def quantization_options(mode="none"):
    mode = mode.lower()
    if mode == "none":
        return {}
    if mode == "8bit":
        return {"load_in_8bit": True}
    if mode == "4bit":
        return {"load_in_4bit": True}
    raise ValueError("mode must be none, 8bit, or 4bit")
