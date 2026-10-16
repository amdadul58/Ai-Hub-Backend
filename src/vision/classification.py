def classify_image(image, classifier):
    if not callable(classifier):
        raise TypeError("classifier must be callable.")
    result = classifier(image)
    return {"task": "image_classification", "result": result}
