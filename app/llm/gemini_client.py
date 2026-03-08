import google.generativeai as genai
from app.llm.base_llm import BaseLLM
from app.core.config import settings


class GeminiClient(BaseLLM):

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def generate_sql(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def generate_answer(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()