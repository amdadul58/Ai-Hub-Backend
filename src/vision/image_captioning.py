def caption_image(image, captioner):
    if not callable(captioner):
        raise TypeError("captioner must be callable.")
    result = captioner(image)
    return {"task": "image_captioning", "caption": result}
