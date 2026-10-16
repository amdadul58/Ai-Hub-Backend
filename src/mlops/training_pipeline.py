def run_training(estimator, X_train, y_train, X_validation=None, y_validation=None, scorer=None):
    """Fit an estimator and optionally calculate a caller-provided validation score."""
    estimator.fit(X_train, y_train)
    result = {"status": "trained", "model_type": type(estimator).__name__}
    if X_validation is not None and y_validation is not None:
        predictions = estimator.predict(X_validation)
        if scorer is not None:
            result["validation_score"] = float(scorer(y_validation, predictions))
        result["validation_samples"] = len(y_validation)
    return {"model": estimator, "report": result}
