from google import genai
from app.llm.base_llm import BaseLLM
from app.core.config import settings


class GeminiClient(BaseLLM):

    def __init__(self):
        self.model = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate_sql(self, prompt: str) -> str:
        response = self.model.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()

    def generate_answer(self, prompt: str) -> str:
        response = self.model.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()

    def generate_title(self, prompt: str) -> str:
        response = self.model.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()