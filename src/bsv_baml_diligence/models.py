from __future__ import annotations

import os
from enum import Enum
from typing import Any, Literal

os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "1")

from pydantic import BaseModel, Field


class Category(str, Enum):
    BUG = "bug"
    OUTAGE = "outage"
    BILLING = "billing"
    SECURITY = "security"
    FEATURE_REQUEST = "feature_request"
    DATA_LOSS = "data_loss"
    INTEGRATION_FAILURE = "integration_failure"
    PERFORMANCE = "performance"
    ACCOUNT_ACCESS = "account_access"
    COMPLIANCE_PRIVACY = "compliance_privacy"
    HOW_TO = "how_to"
    UNCLEAR = "unclear"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Team(str, Enum):
    SUPPORT = "support"
    ENGINEERING = "engineering"
    SECURITY = "security"
    BILLING = "billing"
    CUSTOMER_SUCCESS = "customer_success"
    COMPLIANCE = "compliance"


class Ticket(BaseModel):
    ticket_id: str
    scenario: str
    subject: str
    body: str
    expected_category: Category
    expected_urgency: Urgency
    expected_team: Team
    expected_needs_human_review: bool
    expected_reason: str

    @property
    def text(self) -> str:
        return f"Subject: {self.subject}\n\n{self.body}"


class TicketClassification(BaseModel):
    category: Category = Field(description="Best ticket category")
    urgency: Urgency = Field(description="Business urgency based only on the ticket text")
    team: Team = Field(description="First team that should own the ticket")
    needs_human_review: bool = Field(
        description="True for security, data loss, compliance, critical escalation, billing disputes, or ambiguous cases"
    )
    rationale: str = Field(description="Short grounded reason for the classification")


class TicketFacts(BaseModel):
    summary: str = Field(description="One sentence summary grounded in the ticket")
    grounded_facts: list[str] = Field(description="Concrete facts explicitly stated in the ticket")
    missing_information: list[str] = Field(description="Information needed before resolving the issue; empty if none")
    customer_impact: str = Field(description="Impact on customer users, revenue, security, compliance, or operations")
    risk_signals: list[str] = Field(description="Signals such as production impact, renewal pressure, security exposure, data loss, or ambiguity")


class DraftResponse(BaseModel):
    draft_response: str = Field(description="Customer-facing support reply that does not invent facts or overpromise")
    tone: Literal["calm", "apologetic", "clarifying", "escalation"] = Field(description="Tone used in the reply")
    promised_actions: list[str] = Field(description="Only actions safely promised by the response")
    safety_notes: list[str] = Field(description="Internal notes about uncertainty, escalation, or things not to claim")


class StepResult(BaseModel):
    ok: bool
    latency_ms: float | None = None
    parsed: dict[str, Any] | None = None
    raw_text: str | None = None
    usage_metadata: dict[str, Any] | None = None
    error: str | None = None


class RunOutput(BaseModel):
    implementation: str
    ticket_id: str
    run_index: int
    model: str
    steps: dict[str, StepResult]
