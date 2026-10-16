import pytest

from src.llm.generation import TextGenerator


class FakeInference:
    def __init__(self):
        self.received_prompt = None

    def generate(self, prompt):
        self.received_prompt = prompt
        return "generated response"


def test_generator_requires_configured_inference():
    generator = TextGenerator()

    with pytest.raises(RuntimeError, match="No inference model configured"):
        generator.generate("Hello")


def test_generator_uses_inference_and_returns_response():
    inference = FakeInference()
    generator = TextGenerator(inference=inference)

    result = generator.generate("Hello")

    assert result == "generated response"
    assert "Hello" in inference.received_prompt
    assert "Assistant:" in inference.received_prompt


def test_generator_accepts_custom_system_prompt():
    inference = FakeInference()
    generator = TextGenerator(inference=inference)

    generator.generate("Test prompt", system_prompt="Be concise.")

    assert inference.received_prompt.startswith("Be concise.")