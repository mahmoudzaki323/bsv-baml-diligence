from __future__ import annotations

import json
from typing import Any

from .models import Category, Team, Ticket, Urgency

CATEGORY_VALUES = [item.value for item in Category]
URGENCY_VALUES = [item.value for item in Urgency]
TEAM_VALUES = [item.value for item in Team]
TONE_VALUES = ["calm", "apologetic", "clarifying", "escalation"]


def _json_blob(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def classification_prompt(ticket: Ticket) -> str:
    return f"""
You are a support operations triage assistant for a B2B SaaS company.
Classify the ticket using only facts in the ticket. Do not infer facts that are not stated.
Use unclear when the ticket lacks enough concrete detail to route confidently.

Allowed category values: {CATEGORY_VALUES}
Allowed urgency values: {URGENCY_VALUES}
Allowed team values: {TEAM_VALUES}

Ticket:
{ticket.text}
""".strip()


def json_classification_prompt(ticket: Ticket) -> str:
    return f"""
{classification_prompt(ticket)}

Return only valid JSON with this exact shape:
{{
  "category": one of {CATEGORY_VALUES},
  "urgency": one of {URGENCY_VALUES},
  "team": one of {TEAM_VALUES},
  "needs_human_review": boolean,
  "rationale": "short grounded reason"
}}
""".strip()


def facts_prompt(ticket: Ticket, classification: dict[str, Any]) -> str:
    return f"""
You are extracting grounded support facts. Separate explicit facts from missing information.
Do not add facts from general product knowledge. Do not assume root cause.

Ticket:
{ticket.text}

Current classification:
{_json_blob(classification)}
""".strip()


def json_facts_prompt(ticket: Ticket, classification: dict[str, Any]) -> str:
    return f"""
{facts_prompt(ticket, classification)}

Return only valid JSON with this exact shape:
{{
  "summary": "one sentence summary grounded in the ticket",
  "grounded_facts": ["explicitly stated fact"],
  "missing_information": ["missing detail needed to resolve"],
  "customer_impact": "impact on customer users, revenue, security, compliance, or operations",
  "risk_signals": ["risk signal explicitly supported by the ticket"]
}}
""".strip()


def draft_prompt(ticket: Ticket, classification: dict[str, Any], facts: dict[str, Any]) -> str:
    return f"""
You are drafting a safe customer-facing support response for a B2B SaaS company.
Do not promise a refund, fix, root cause, SLA, legal conclusion, or security determination unless explicitly supported.
If the issue is ambiguous, ask for the minimum useful clarification.
If human review is required, acknowledge escalation without claiming resolution.

Ticket:
{ticket.text}

Classification:
{_json_blob(classification)}

Extracted facts:
{_json_blob(facts)}
""".strip()


def json_draft_prompt(ticket: Ticket, classification: dict[str, Any], facts: dict[str, Any]) -> str:
    return f"""
{draft_prompt(ticket, classification, facts)}

Allowed tone values: {TONE_VALUES}

Return only valid JSON with this exact shape:
{{
  "draft_response": "customer-facing support reply",
  "tone": one of {TONE_VALUES},
  "promised_actions": ["only actions safely promised by the response"],
  "safety_notes": ["internal note about uncertainty, escalation, or things not to claim"]
}}
""".strip()
