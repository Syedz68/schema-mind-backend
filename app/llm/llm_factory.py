from app.utils.enums import LlmMode
from app.llm.gemini_client import GeminiClient
from app.llm.ollama_client import OllamaClient


class LLMFactory:

    @staticmethod
    def get_llm(mode: LlmMode):

        if mode == LlmMode.online:
            return GeminiClient()

        if mode == LlmMode.local:
            return OllamaClient()

        raise ValueError("Unsupported LLM mode")