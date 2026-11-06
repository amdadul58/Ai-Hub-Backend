import ollama


class OllamaCloudInference:
    """Inference provider for Ollama Cloud via the authenticated local Ollama service."""

    provider = "ollama_cloud"

    def __init__(self, model="gemma4:31b-cloud"):
        self.model_name = model
        self.client = ollama.Client(
            host="http://127.0.0.1:11434"
        )

    def generate(self, prompt, system_prompt=None, max_new_tokens=None):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []

        if system_prompt and system_prompt.strip():
            messages.append({
                "role": "system",
                "content": system_prompt.strip(),
            })

        messages.append({
            "role": "user",
            "content": prompt.strip(),
        })

        options = {}
        if max_new_tokens is not None:
            options["num_predict"] = max_new_tokens

        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            stream=False,
            options=options or None,
        )

        answer = response.message.content
        if not answer or not answer.strip():
            raise ValueError("Ollama Cloud returned an empty response.")

        return answer.strip()
