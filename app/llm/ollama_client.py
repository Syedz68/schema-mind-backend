import requests
from app.llm.base_llm import BaseLLM


class OllamaClient(BaseLLM):

    def __init__(self, model="qwen2.5"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate_sql(self, prompt: str) -> str:

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]

    def generate_answer(self, prompt: str) -> str:

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]

    def generate_title(self, prompt: str) -> str:

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]