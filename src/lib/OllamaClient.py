import ollama
import dotenv
import os
import json
from pydantic import BaseModel

dotenv.load_dotenv()


class ValidationResult(BaseModel):
    valid: bool
    reason: str


class OllamaClient:
    def __init__(
        self,
        base_url: str = os.getenv("OLLAMA_URL"),
        model: str = os.getenv("OLLAMA_MODEL"),
        system_prompt_file_path: str = os.getenv("SYSTEM_PROMPT_PATH"),
    ):
        self.ollama_url = base_url
        self.ollama_model = model
        self.system_prompt = self.read_system_prompt(system_prompt_file_path)
        self.ollama_client = ollama.Client(host=self.ollama_url)

    def read_system_prompt(self, system_prompt_file_path: str) -> str:
        """讀取系統提示詞"""
        with open(system_prompt_file_path, "r") as file:
            return file.read()

    def get_validation_result(self, message: dict) -> ValidationResult:
        """發送請求到 Ollama"""
        response = self.ollama_client.chat(
            model=self.ollama_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": json.dumps(message, ensure_ascii=False)},
            ],
            options={"temperature": 0.0},
            format=ValidationResult.model_json_schema(),
        )
        llm_response = ValidationResult.model_validate_json(response.message.content)

        return llm_response
