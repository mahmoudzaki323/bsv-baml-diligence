from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any, TypeVar

os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "1")

from pydantic import BaseModel

from .io_utils import require_google_key

T = TypeVar("T", bound=BaseModel)


def client() -> str:
    require_google_key()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is required.")
    return api_key


def call_structured(
    api_key: str,
    model: str,
    prompt: str,
    schema: type[T],
) -> tuple[T, str, float, dict[str, Any] | None]:
    start = time.perf_counter()
    response = _generate_content(
        api_key=api_key,
        model=model,
        prompt=prompt,
        generation_config={
            "temperature": 0.1,
            "responseMimeType": "application/json",
            "responseJsonSchema": schema.model_json_schema(),
        },
    )
    latency_ms = (time.perf_counter() - start) * 1000
    raw_text = _extract_text(response)
    parsed = schema.model_validate_json(raw_text)
    return parsed, raw_text, latency_ms, response.get("usageMetadata")


def call_json(
    api_key: str,
    model: str,
    prompt: str,
    schema: type[T],
) -> tuple[T, str, float, dict[str, Any] | None]:
    start = time.perf_counter()
    response = _generate_content(
        api_key=api_key,
        model=model,
        prompt=prompt,
        generation_config={
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    )
    latency_ms = (time.perf_counter() - start) * 1000
    raw_text = _extract_text(response)
    parsed_json = _parse_json(raw_text)
    parsed = schema.model_validate(parsed_json)
    return parsed, raw_text, latency_ms, response.get("usageMetadata")


def _generate_content(api_key: str, model: str, prompt: str, generation_config: dict[str, Any]) -> dict[str, Any]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = json.dumps(
        {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": generation_config,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API HTTP {exc.code}: {body}") from exc


def _extract_text(response: dict[str, Any]) -> str:
    candidates = response.get("candidates") or []
    if not candidates:
        raise ValueError(f"Gemini response did not include candidates: {response}")
    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    if not text_parts:
        raise ValueError(f"Gemini response did not include text parts: {response}")
    return "\n".join(text_parts)


def _parse_json(raw_text: str) -> Any:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return json.loads(fenced.group(1))

    first = raw_text.find("{")
    last = raw_text.rfind("}")
    if first >= 0 and last > first:
        return json.loads(raw_text[first : last + 1])

    raise ValueError("Model response did not contain parseable JSON.")
