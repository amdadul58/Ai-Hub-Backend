from src.llm.guardrails import validate_input
from src.llm.prompt_manager import PromptManager


class TextGenerator:
    def __init__(self, inference=None, prompt_manager=None):
        self.inference = inference
        self.prompt_manager = prompt_manager or PromptManager()

    def generate(self, prompt, system_prompt=None):
        if self.inference is None:
            raise RuntimeError("No inference model configured.")

        user_text = validate_input(prompt)

        if system_prompt is None:
            system = self.prompt_manager.get()
        else:
            system = validate_input(system_prompt, max_chars=4000)

        if getattr(self.inference, "provider", None) == "ollama_cloud":
            return self.inference.generate(
                user_text,
                system_prompt=system,
            )

        model = getattr(self.inference, "model", None)
        config = getattr(model, "config", None)

        if getattr(config, "is_encoder_decoder", False):
            combined = (
                f"{system}\n\n"
                f"Question: {user_text}\n"
                "Give a clear, accurate answer in simple English. "
                "Answer the question directly and include an example when useful."
            )
        else:
            combined = f"{system}\n\nUser: {user_text}\nAssistant:"

        return self.inference.generate(combined)
