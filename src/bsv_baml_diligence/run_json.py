from __future__ import annotations

from .gemini_api import call_json, client
from .io_utils import benchmark_model, output_path, read_json, serialize, write_json
from .models import DraftResponse, StepResult, Ticket, TicketClassification, TicketFacts
from .prompts import json_classification_prompt, json_draft_prompt, json_facts_prompt

IMPLEMENTATION = "gemini_json"


def run_ticket(ticket: Ticket, run_index: int, force: bool = False) -> dict:
    path = output_path(IMPLEMENTATION, ticket.ticket_id, run_index)
    if path.exists() and not force:
        return read_json(path)

    model = benchmark_model()
    genai_client = client()
    steps: dict[str, StepResult] = {}

    classification = None
    try:
        classification, raw, latency, usage = call_json(
            genai_client, model, json_classification_prompt(ticket), TicketClassification
        )
        steps["classification"] = StepResult(
            ok=True, latency_ms=latency, parsed=serialize(classification), raw_text=raw, usage_metadata=usage
        )
    except Exception as exc:
        steps["classification"] = StepResult(ok=False, error=repr(exc))

    facts = None
    if classification is not None:
        try:
            facts, raw, latency, usage = call_json(
                genai_client, model, json_facts_prompt(ticket, serialize(classification)), TicketFacts
            )
            steps["facts"] = StepResult(ok=True, latency_ms=latency, parsed=serialize(facts), raw_text=raw, usage_metadata=usage)
        except Exception as exc:
            steps["facts"] = StepResult(ok=False, error=repr(exc))
    else:
        steps["facts"] = StepResult(ok=False, error="Skipped because classification failed.")

    if classification is not None and facts is not None:
        try:
            draft, raw, latency, usage = call_json(
                genai_client, model, json_draft_prompt(ticket, serialize(classification), serialize(facts)), DraftResponse
            )
            steps["draft"] = StepResult(ok=True, latency_ms=latency, parsed=serialize(draft), raw_text=raw, usage_metadata=usage)
        except Exception as exc:
            steps["draft"] = StepResult(ok=False, error=repr(exc))
    else:
        steps["draft"] = StepResult(ok=False, error="Skipped because an earlier step failed.")

    output = {
        "implementation": IMPLEMENTATION,
        "ticket_id": ticket.ticket_id,
        "run_index": run_index,
        "model": model,
        "steps": serialize(steps),
    }
    write_json(path, output)
    return output
