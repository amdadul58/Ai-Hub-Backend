import argparse
import json
import sys
from pathlib import Path

# Add the project root so that Python can find the src package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

from src.machine_learning.algorithms.classification import make_classifier
from src.machine_learning.training.trainer import train_model
from src.machine_learning.evaluation.metrics import classification_metrics


def main():
    parser = argparse.ArgumentParser(
        description="Train a small CPU-friendly ML demonstration model."
    )
    parser.add_argument(
        "--model",
        choices=["logistic_regression", "decision_tree", "random_forest"],
        default="logistic_regression",
    )
    args = parser.parse_args()

    dataset = load_breast_cancer()
    X_train, X_test, y_train, y_test = train_test_split(
        dataset.data,
        dataset.target,
        test_size=0.2,
        random_state=42,
        stratify=dataset.target,
    )

    model_path = (
        PROJECT_ROOT / "artifacts" / "models" / f"{args.model}.joblib"
    )

    model = make_classifier(args.model)
    result = train_model(model, X_train, y_train, model_path)
    predictions = result["model"].predict(X_test)
    metrics = classification_metrics(y_test, predictions)

    report = {
        "model": args.model,
        "dataset": "sklearn_breast_cancer",
        "train_samples": len(y_train),
        "test_samples": len(y_test),
        "model_path": result["model_path"],
        "metrics": metrics,
    }

    report_path = (
        PROJECT_ROOT / "artifacts" / "models" / f"{args.model}_metrics.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
