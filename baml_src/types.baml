enum Category {
  BUG @alias("bug") @description("A product defect with specific broken behavior")
  OUTAGE @alias("outage") @description("A production service or workflow is unavailable")
  BILLING @alias("billing") @description("Payment, invoice, refund, or subscription issue")
  SECURITY @alias("security") @description("Potential vulnerability, abuse, or security incident")
  FEATURE_REQUEST @alias("feature_request") @description("Product enhancement request")
  DATA_LOSS @alias("data_loss") @description("Missing, deleted, corrupted, or unrecovered data")
  INTEGRATION_FAILURE @alias("integration_failure") @description("External integration, sync, API, webhook, or connector failure")
  PERFORMANCE @alias("performance") @description("Latency, slow loading, degraded speed, or throughput issue")
  ACCOUNT_ACCESS @alias("account_access") @description("Login, invite, permission, or workspace access issue")
  COMPLIANCE_PRIVACY @alias("compliance_privacy") @description("DPA, privacy, compliance, retention, or subprocessors")
  HOW_TO @alias("how_to") @description("Usage question or request for product guidance")
  UNCLEAR @alias("unclear") @description("Not enough facts to route confidently")
}

enum Urgency {
  LOW @alias("low") @description("No immediate user or business impact")
  MEDIUM @alias("medium") @description("Limited impact or workaround exists")
  HIGH @alias("high") @description("Important customer workflow affected")
  CRITICAL @alias("critical") @description("Production outage, security risk, data loss, or major business impact")
}

enum Team {
  SUPPORT @alias("support") @description("Frontline support or product guidance")
  ENGINEERING @alias("engineering") @description("Product engineering or infrastructure support")
  SECURITY @alias("security") @description("Security response team")
  BILLING @alias("billing") @description("Billing, payments, or finance operations")
  CUSTOMER_SUCCESS @alias("customer_success") @description("Customer success or account management")
  COMPLIANCE @alias("compliance") @description("Privacy, legal, or compliance team")
}

class TicketClassification {
  category Category @description("Best ticket category")
  urgency Urgency @description("Business urgency based only on the ticket text")
  team Team @description("First team that should own the ticket")
  needs_human_review bool @description("True for security, data loss, compliance, critical escalation, billing disputes, or ambiguous cases")
  rationale string @description("Short grounded reason for the classification")
}

class TicketFacts {
  summary string @description("One sentence summary grounded in the ticket")
  grounded_facts string[] @description("Concrete facts explicitly stated in the ticket")
  missing_information string[] @description("Information needed before resolving the issue; empty if none")
  customer_impact string @description("Impact on customer users, revenue, security, compliance, or operations")
  risk_signals string[] @description("Signals such as production impact, renewal pressure, security exposure, data loss, or ambiguity")
}

class DraftResponse {
  draft_response string @description("Customer-facing support reply that does not invent facts or overpromise")
  tone "calm" | "apologetic" | "clarifying" | "escalation" @description("Tone used in the reply")
  promised_actions string[] @description("Only actions safely promised by the response")
  safety_notes string[] @description("Internal notes about uncertainty, escalation, or things not to claim")
}
