from __future__ import annotations

import json
import re
import time
from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from .io_utils import require_google_key, usage_to_dict

T = TypeVar("T", bound=BaseModel)


def client() -> genai.Client:
    require_google_key()
    return genai.Client()


def call_structured(
    genai_client: genai.Client,
    model: str,
    prompt: str,
    schema: type[T],
) -> tuple[T, str, float, dict[str, Any] | None]:
    start = time.perf_counter()
    response = genai_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1,
        ),
    )
    latency_ms = (time.perf_counter() - start) * 1000
    parsed = schema.model_validate_json(response.text)
    return parsed, response.text, latency_ms, usage_to_dict(response)


def call_json(
    genai_client: genai.Client,
    model: str,
    prompt: str,
    schema: type[T],
) -> tuple[T, str, float, dict[str, Any] | None]:
    start = time.perf_counter()
    response = genai_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    latency_ms = (time.perf_counter() - start) * 1000
    raw_text = response.text
    parsed_json = _parse_json(raw_text)
    parsed = schema.model_validate(parsed_json)
    return parsed, raw_text, latency_ms, usage_to_dict(response)


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
