function ClassifyTicket(ticket: string) -> TicketClassification {
  client Gemini
  prompt #"
    {{ _.role("system") }}
    You are a support operations triage assistant for a B2B SaaS company.
    Classify the ticket using only facts in the ticket. Do not infer facts that are not stated.
    Use UNCLEAR when the ticket lacks enough concrete detail to route confidently.

    {{ _.role("user") }}
    Ticket:
    {{ ticket }}

    {{ ctx.output_format }}
  "#
}

function ExtractTicketFacts(ticket: string, classification: TicketClassification) -> TicketFacts {
  client Gemini
  prompt #"
    {{ _.role("system") }}
    Extract grounded support facts from the ticket. Separate explicit facts from missing information.
    Do not add facts from general product knowledge. Do not assume root cause.

    {{ _.role("user") }}
    Ticket:
    {{ ticket }}

    Current classification:
    {{ classification }}

    {{ ctx.output_format }}
  "#
}

function DraftSupportResponse(ticket: string, classification: TicketClassification, facts: TicketFacts) -> DraftResponse {
  client Gemini
  prompt #"
    {{ _.role("system") }}
    Draft a safe support response for a B2B SaaS customer.
    Do not promise a refund, fix, root cause, SLA, legal conclusion, or security determination unless explicitly supported.
    If the issue is ambiguous, ask for the minimum useful clarification.
    If human review is required, acknowledge escalation without claiming resolution.

    {{ _.role("user") }}
    Ticket:
    {{ ticket }}

    Classification:
    {{ classification }}

    Extracted facts:
    {{ facts }}

    {{ ctx.output_format }}
  "#
}
