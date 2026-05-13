from __future__ import annotations

import json
import os
import time
from enum import Enum
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

from .models import Ticket

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
RAW_DIR = OUTPUTS_DIR / "raw"
COMPARISON_DIR = OUTPUTS_DIR / "comparison"
CHARTS_DIR = ROOT / "artifacts" / "charts"
DOCS_DIR = ROOT / "docs"


def load_environment() -> None:
    load_dotenv(ROOT / ".env")


def benchmark_model() -> str:
    load_environment()
    model = os.getenv("BENCHMARK_MODEL")
    if not model:
        raise RuntimeError("Set BENCHMARK_MODEL in .env or the shell before running the benchmark.")
    return model


def require_openai_key() -> None:
    load_environment()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY in .env or the shell before running OpenAI calls.")


def ensure_output_dirs() -> None:
    for path in [RAW_DIR, COMPARISON_DIR, CHARTS_DIR, DOCS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_tickets(limit: int | None = None) -> list[Ticket]:
    raw = json.loads((DATA_DIR / "tickets.json").read_text())
    tickets = [Ticket.model_validate(item) for item in raw]
    if limit is not None:
        return tickets[:limit]
    return tickets


def serialize(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return value


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(serialize(data), indent=2, sort_keys=True) + "\n"
    for attempt in range(3):
        try:
            path.write_text(payload)
            return
        except TimeoutError:
            if attempt == 2:
                raise
            time.sleep(1)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def output_path(implementation: str, ticket_id: str, run_index: int) -> Path:
    return RAW_DIR / implementation / ticket_id / f"run_{run_index:02d}.json"


def usage_to_dict(response: Any) -> dict[str, Any] | None:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json")
    if hasattr(usage, "dict"):
        return usage.dict()
    if isinstance(usage, dict):
        return usage
    return {"repr": repr(usage)}
