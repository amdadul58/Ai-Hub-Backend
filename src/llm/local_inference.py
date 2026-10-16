import torch
from src.llm.guardrails import validate_input
from src.llm.output_validation import validate_output

class LocalInference:
    def __init__(self, tokenizer, model, max_new_tokens=128):
        self.tokenizer = tokenizer
        self.model = model
        self.max_new_tokens = max_new_tokens
        self.model.eval()

    def generate(self, prompt):
        prompt = validate_input(prompt)
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.inference_mode():
            output = self.model.generate(
                **inputs, max_new_tokens=self.max_new_tokens
            )
        text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return validate_output(text)
