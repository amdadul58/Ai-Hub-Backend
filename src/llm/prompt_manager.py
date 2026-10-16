from src.llm.prompt_templates import DEFAULT_SYSTEM_PROMPT

class PromptManager:
    def __init__(self):
        self.prompts = {"default": DEFAULT_SYSTEM_PROMPT}

    def get(self, name="default"):
        if name not in self.prompts:
            raise KeyError(f"Unknown prompt: {name}")
        return self.prompts[name]

    def register(self, name, prompt):
        if not name.strip() or not prompt.strip():
            raise ValueError("Prompt name and content are required")
        self.prompts[name] = prompt
