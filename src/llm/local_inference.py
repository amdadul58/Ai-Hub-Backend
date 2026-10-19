class LocalInference:
    def __init__(self, model, tokenizer, max_new_tokens=128):
        self.model = model
        self.tokenizer = tokenizer
        self.max_new_tokens = max(1, min(int(max_new_tokens), 512))

    def generate(self, prompt: str, max_new_tokens=None) -> str:
        import torch

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        token_limit = self.max_new_tokens if max_new_tokens is None else max(
            1, min(int(max_new_tokens), 512)
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        device = getattr(self.model, "device", None)
        if device is not None:
            inputs = inputs.to(device)

        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=token_limit,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        if getattr(self.model.config, "is_encoder_decoder", False):
            generated_ids = output_ids
        else:
            generated_ids = output_ids[:, inputs["input_ids"].shape[1]:]

        result = self.tokenizer.decode(
            generated_ids[0], skip_special_tokens=True
        ).strip()

        if not result:
            raise ValueError("The model returned an empty response.")
        return result
