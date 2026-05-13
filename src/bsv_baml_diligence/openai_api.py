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

from .io_utils import require_openai_key

T = TypeVar("T", bound=BaseModel)
Message = dict[str, str]


def client() -> str:
    require_openai_key()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required.")
    return api_key


def call_structured(
    api_key: str,
    model: str,
    prompt: str | list[Message],
    schema: type[T],
) -> tuple[T, str, float, dict[str, Any] | None]:
    start = time.perf_counter()
    response = _chat_completion(
        api_key=api_key,
        model=model,
        prompt=prompt,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": _strict_json_schema(schema.model_json_schema()),
                "strict": True,
            },
        },
    )
    latency_ms = (time.perf_counter() - start) * 1000
    raw_text = _extract_text(response)
    parsed = schema.model_validate_json(raw_text)
    return parsed, raw_text, latency_ms, response.get("usage")


def call_json(
    api_key: str,
    model: str,
    prompt: str | list[Message],
    schema: type[T],
) -> tuple[T, str, float, dict[str, Any] | None]:
    start = time.perf_counter()
    response = _chat_completion(
        api_key=api_key,
        model=model,
        prompt=prompt,
        response_format={"type": "json_object"},
    )
    latency_ms = (time.perf_counter() - start) * 1000
    raw_text = _extract_text(response)
    parsed_json = _parse_json(raw_text)
    parsed = schema.model_validate(parsed_json)
    return parsed, raw_text, latency_ms, response.get("usage")


def _chat_completion(api_key: str, model: str, prompt: str | list[Message], response_format: dict[str, Any]) -> dict[str, Any]:
    messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "response_format": response_format,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body}") from exc


def _extract_text(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        raise ValueError(f"OpenAI response did not include choices: {response}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise ValueError(f"OpenAI response did not include message content: {response}")
    return content


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


def _strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Make Pydantic JSON Schema acceptable for strict OpenAI structured outputs."""
    cleaned = json.loads(json.dumps(schema))

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if "$ref" in node:
                ref = node["$ref"]
                node.clear()
                node["$ref"] = ref
                return
            if node.get("type") == "object":
                node.setdefault("additionalProperties", False)
                properties = node.get("properties")
                if isinstance(properties, dict):
                    node["required"] = list(properties.keys())
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(cleaned)
    return cleaned
