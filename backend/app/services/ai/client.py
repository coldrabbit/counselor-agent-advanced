import json
import time
import logging

from httpx import Client

from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model

    def chat(self, system_prompt: str, user_message: str, max_retries: int = 2) -> dict:
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        }

        last_error = ""
        for attempt in range(max_retries + 1):
            try:
                with Client(timeout=60) as client:
                    resp = client.post(f"{self.base_url}/v1/chat/completions", headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()

                duration_ms = int((time.time() - start_time) * 1000)
                usage = data.get("usage", {})
                token_usage = usage.get("total_tokens", 0)
                content = data["choices"][0]["message"]["content"]

                logger.info(f"AI call success: model={self.model}, tokens={token_usage}, duration={duration_ms}ms")

                return {
                    "success": True,
                    "content": content,
                    "model": self.model,
                    "token_usage": token_usage,
                    "duration_ms": duration_ms,
                }
            except Exception as e:
                last_error = str(e)
                logger.warning(f"AI call attempt {attempt + 1} failed: {last_error}")
                if attempt < max_retries:
                    time.sleep(1)

        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"AI call failed after {max_retries + 1} attempts: {last_error}")
        return {
            "success": False,
            "content": "",
            "model": self.model,
            "token_usage": 0,
            "duration_ms": duration_ms,
            "error": last_error,
        }

