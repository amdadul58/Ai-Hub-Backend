def synthesize(text, synthesizer, output_path=None, voice=None):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text cannot be empty.")
    if not callable(synthesizer):
        raise TypeError("synthesizer must be callable.")
    result = synthesizer(text.strip(), output_path=output_path, voice=voice)
    return {"text": text.strip(), "output": result}
