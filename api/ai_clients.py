import json
from typing import Any

import requests
from google import genai
from google.genai import types

from api import config


class AIClientError(RuntimeError):
    pass


class GeminiAdapter:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise AIClientError("GOOGLE_API_KEY is not configured.")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_json(self, prompt: str, schema: dict[str, Any], temperature: float = 0.1) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=temperature,
            ),
        )
        return json.loads(response.text)

    def generate_text(
        self,
        user_prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
    ) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        )
        return response.text


class OpenRouterAdapter:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise AIClientError("OPENROUTER_API_KEY is not configured.")
        self.api_key = api_key
        self.model = model

    def _chat(self, messages: list[dict[str, str]], extra: dict[str, Any] | None = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": config.OPENROUTER_SITE_URL,
            "X-Title": config.OPENROUTER_APP_NAME,
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if extra:
            payload.update(extra)
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90,
        )
        if response.status_code >= 400:
            raise AIClientError(f"OpenRouter error {response.status_code}: {response.text}")
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIClientError("OpenRouter returned an unexpected response shape.") from exc

    def generate_json(self, prompt: str, schema: dict[str, Any], temperature: float = 0.1) -> dict[str, Any]:
        content = self._chat(
            [{"role": "user", "content": prompt}],
            {
                "temperature": temperature,
                "response_format": {"type": "json_object"},
            },
        )
        content = content.strip()
        if content.startswith("```"):
            content = content.removeprefix("```json").removeprefix("```").strip()
            content = content.removesuffix("```").strip()
        return json.loads(content)

    def generate_text(
        self,
        user_prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
    ) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": user_prompt})
        return self._chat(
            messages,
            {
                "temperature": temperature,
                "max_tokens": max_output_tokens,
            },
        )


def client_for_tier(tier: str):
    if tier == "owner":
        return GeminiAdapter(config.GOOGLE_API_KEY, config.OWNER_MODEL)
    return OpenRouterAdapter(config.OPENROUTER_API_KEY, config.PAID_MODEL)
