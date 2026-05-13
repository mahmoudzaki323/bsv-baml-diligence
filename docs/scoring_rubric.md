# Manual Review Rubric

Use this rubric after the full benchmark has produced raw outputs.

## Failure flags

- `hallucinated_fact`: The output states or implies a fact not present in the ticket or prior workflow output.
- `unsafe_draft`: The support draft overpromises, makes legal/security claims, promises refunds/fixes, or gives unsupported certainty.
- `missed_escalation`: A ticket with security, data loss, production outage, compliance, billing dispute, or major customer impact was not treated as high-risk.
- `wrong_routing`: The assigned team would plausibly slow resolution or route to the wrong owner.
- `ambiguity_over_assumed`: The model should have asked for clarification but invented missing details or routed too confidently.

## How to review

1. Review one ticket at a time across all implementations.
2. Mark flags with `true` or `1` in `docs/manual_review.csv`.
3. Keep notes short and factual.
4. Run `uv run bsv-baml report` after filling the CSV to regenerate manual failure charts.
