from __future__ import annotations

from collections.abc import Callable

from .io_utils import ensure_output_dirs, load_tickets
from .models import Ticket
from .run_baml import run_ticket as run_baml_ticket
from .run_json import run_ticket as run_json_ticket
from .run_structured import run_ticket as run_structured_ticket

Runner = Callable[[Ticket, int, bool], dict]

RUNNERS: dict[str, Runner] = {
    "baml": run_baml_ticket,
    "gemini_structured": run_structured_ticket,
    "gemini_json": run_json_ticket,
}


def run_all(runs: int, ticket_limit: int | None = None, force: bool = False, implementations: list[str] | None = None) -> None:
    ensure_output_dirs()
    tickets = load_tickets(ticket_limit)
    selected = implementations or list(RUNNERS)
    for implementation in selected:
        runner = RUNNERS[implementation]
        for ticket in tickets:
            for run_index in range(1, runs + 1):
                runner(ticket, run_index, force)
