from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate_sql(self, prompt: str) -> str:
        pass

    @abstractmethod
    def generate_answer(self, prompt: str) -> str:
        pass