import json
import logging
import os
from typing import TYPE_CHECKING

import dotenv
import ollama
from pydantic import BaseModel

from src.prompt.system_prompts import (
    validate_humanresource_prompt,
    validate_supplies_prompt,
)

if TYPE_CHECKING:
    from .GfApiClient import HumanResource, Supplies

logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class ValidationResult(BaseModel):
    valid: bool
    reason: str


class OllamaClient:
    def __init__(
        self,
        base_url: str = os.getenv("OLLAMA_URL"),
        model: str = os.getenv("OLLAMA_MODEL"),
    ):
        self.ollama_url = base_url
        self.ollama_model = model
        self.ollama_client = ollama.Client(host=self.ollama_url)

    def get_validation_result(self, message: "HumanResource | Supplies", resource_type: str) -> ValidationResult:
        """發送請求到 Ollama"""
        system_prompt = self.get_system_prompt(resource_type)

        message_dict = message.model_dump() if hasattr(message, "model_dump") else message

        response = self.ollama_client.chat(
            model=self.ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(message_dict, ensure_ascii=False)},
            ],
            options={"temperature": 0.0},
            format=ValidationResult.model_json_schema(),
        )
        llm_response = ValidationResult.model_validate_json(response.message.content)
        logger.info(f"validation result: {llm_response.valid}")

        return llm_response

    def get_system_prompt(self, resource_type: str) -> str:
        if resource_type == "human_resource":
            return validate_humanresource_prompt
        elif resource_type == "supplies":
            return validate_supplies_prompt
        else:
            raise ValueError(f"Invalid resource type: {resource_type}")
