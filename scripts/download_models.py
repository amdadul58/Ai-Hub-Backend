import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Inspect model files without downloading large weights."
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Reserved for an explicitly configured model downloader.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    model_dir = root / "artifacts" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    print(f"Model directory: {model_dir}")
    existing = list(model_dir.glob("*"))
    if existing:
        print("Existing model artifacts:")
        for item in existing:
            print(f"  {item.name} ({item.stat().st_size} bytes)")
    else:
        print("No model artifacts found.")

    if args.download:
        print("No download source is configured. Nothing was downloaded.")
        return 2

    print("Safe inspection only; no model weights were downloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
