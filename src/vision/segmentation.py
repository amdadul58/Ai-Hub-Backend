def segment_image(image, segmenter):
    if not callable(segmenter):
        raise TypeError("segmenter must be callable.")
    return {"task": "image_segmentation", "result": segmenter(image)}
