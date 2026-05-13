from __future__ import annotations

import sys
import time

from .io_utils import ROOT, benchmark_model, load_environment, output_path, read_json, require_google_key, serialize, write_json
from .models import StepResult, Ticket

IMPLEMENTATION = "baml"


def run_ticket(ticket: Ticket, run_index: int, force: bool = False) -> dict:
    path = output_path(IMPLEMENTATION, ticket.ticket_id, run_index)
    if path.exists() and not force:
        return read_json(path)

    load_environment()
    require_google_key()
    model = benchmark_model()
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from baml_client import b

    steps: dict[str, StepResult] = {}

    classification = None
    try:
        start = time.perf_counter()
        classification = b.ClassifyTicket(ticket.text)
        latency = (time.perf_counter() - start) * 1000
        steps["classification"] = StepResult(ok=True, latency_ms=latency, parsed=serialize(classification))
    except Exception as exc:
        steps["classification"] = StepResult(ok=False, error=repr(exc))

    facts = None
    if classification is not None:
        try:
            start = time.perf_counter()
            facts = b.ExtractTicketFacts(ticket.text, classification)
            latency = (time.perf_counter() - start) * 1000
            steps["facts"] = StepResult(ok=True, latency_ms=latency, parsed=serialize(facts))
        except Exception as exc:
            steps["facts"] = StepResult(ok=False, error=repr(exc))
    else:
        steps["facts"] = StepResult(ok=False, error="Skipped because classification failed.")

    if classification is not None and facts is not None:
        try:
            start = time.perf_counter()
            draft = b.DraftSupportResponse(ticket.text, classification, facts)
            latency = (time.perf_counter() - start) * 1000
            steps["draft"] = StepResult(ok=True, latency_ms=latency, parsed=serialize(draft))
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
