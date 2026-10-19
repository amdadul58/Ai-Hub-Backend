import json
import sys
from pathlib import Path

# Reuse AI packages from the previous project; no package download.
OLD_SITE_PACKAGES = (
    Path(r"D:\Ai Eng 26.2\llm-fine-tuning-lab\.venv")
    / "Lib" / "site-packages"
)
if OLD_SITE_PACKAGES.is_dir() and str(OLD_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(OLD_SITE_PACKAGES))


def load_local_model(model_path, **kwargs):
    import torch
    from transformers import (
        AutoConfig,
        AutoTokenizer,
        AutoModelForCausalLM,
        AutoModelForSeq2SeqLM,
    )

    path = Path(model_path).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"Local model directory not found: {path}")

    adapter_config = path / "adapter_config.json"

    if adapter_config.is_file():
        from peft import PeftModel

        config_data = json.loads(adapter_config.read_text(encoding="utf-8"))
        base_model_id = config_data.get("base_model_name_or_path")
        if not base_model_id:
            raise ValueError("LoRA adapter config has no base_model_name_or_path.")

        config = AutoConfig.from_pretrained(
            base_model_id, local_files_only=True
        )
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_id, local_files_only=True
        )
        model_class = (
            AutoModelForSeq2SeqLM
            if getattr(config, "is_encoder_decoder", False)
            else AutoModelForCausalLM
        )
        base_model = model_class.from_pretrained(
            base_model_id,
            config=config,
            local_files_only=True,
        )
        model = PeftModel.from_pretrained(
            base_model, str(path), local_files_only=True
        )
    else:
        config = AutoConfig.from_pretrained(str(path), local_files_only=True)
        tokenizer = AutoTokenizer.from_pretrained(
            str(path), local_files_only=True
        )
        model_class = (
            AutoModelForSeq2SeqLM
            if getattr(config, "is_encoder_decoder", False)
            else AutoModelForCausalLM
        )
        model = model_class.from_pretrained(
            str(path), config=config, local_files_only=True, **kwargs
        )

    model.to(torch.device("cpu"))
    model.eval()
    return tokenizer, model
