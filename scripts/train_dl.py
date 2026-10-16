import importlib.util
import sys


def main():
    if importlib.util.find_spec("torch") is None:
        print("PyTorch is not installed in this environment.")
        print("No packages were downloaded or installed.")
        print("For now, the ML training script can run without PyTorch.")
        print("Install a compatible CPU build only when you are ready for DL training.")
        return 2

    import torch

    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print("DL components are available.")
    print("Use the project's trainer functions with a prepared dataset to train a model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
