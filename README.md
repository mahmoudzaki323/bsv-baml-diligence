# BSV BAML Diligence Benchmark

This repo contains a hands-on evaluation of BAML for production-style structured LLM workflows using the OpenAI API.

## Diligence question

Does BAML make structured LLM application logic easier to define, test, debug, and evolve than direct OpenAI API implementations?

## What this benchmark builds

A three-step support ticket triage workflow:

1. Classify ticket category, urgency, team, and human-review requirement.
2. Extract grounded facts, missing information, customer impact, and risk signals.
3. Draft a safe customer-facing support response.

The same workflow is implemented three ways:

1. `baml`: BAML typed functions using the OpenAI provider.
2. `openai_structured`: Direct OpenAI Chat Completions call with strict `json_schema` structured output from the same Pydantic schema.
3. `openai_json`: Direct OpenAI Chat Completions call with JSON mode and manual Pydantic validation.

## Why this is a useful BAML test

The goal is not to prove that BAML makes the model smarter. The goal is to test whether BAML improves the developer workflow once LLM calls become typed, multi-step application logic with expected labels, regression cases, and safety constraints.

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env`:

```bash
OPENAI_API_KEY=your_key_here
BENCHMARK_MODEL=gpt-5.4-nano
```

Generate the BAML Python client:

```bash
uv run baml-cli generate
```

## Run

Smoke test one ticket once across all implementations:

```bash
PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli smoke --force
```

Full benchmark, matching the diligence plan:

```bash
PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli benchmark --runs 5 --force
```

Generate comparison tables and charts:

```bash
MPLBACKEND=Agg PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli report
```

Outputs are written to:

- `outputs/raw/`: raw per-run outputs.
- `outputs/comparison/`: computed CSVs and markdown results table.
- `artifacts/charts/`: charts generated from actual benchmark results.

## Manual review

Automated metrics are not enough for this diligence. Review the outputs and fill `docs/manual_review.csv` using `docs/manual_review.template.csv` and `docs/scoring_rubric.md`.

Then regenerate the report:

```bash
MPLBACKEND=Agg PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli report
```

## Charts

Charts are generated only from observed results, not arbitrary subjective scores:

- `schema_success_rate.png`
- `expected_label_accuracy.png`
- `latency_by_step.png`
- `label_match_by_ticket.png`

`manual_failure_counts.png` is generated only after a reviewer fills the manual review CSV.

## How to read the results

This benchmark is a hands-on diligence artifact, not a definitive model leaderboard. It tests what it is like to build and inspect the same structured workflow through BAML and through direct OpenAI calls.

The strict all-label score is intentionally not the headline metric. It marks a run wrong if any one of four labels differs from the locked expected label. That is useful for spotting disagreements, but it is too brittle for subjective support-ticket triage. The field-level label charts and the raw outputs are more useful for review.

Implementation notes from the corrected run:

- The direct structured-output baseline uses strict JSON schema mode.
- The direct baselines use separate system and user messages to better match BAML's message structure.
- The Pydantic draft-response schema matches BAML's tone constraint.
- The strict schema path required a small schema normalizer because OpenAI rejects `$ref` fields with extra keywords such as field descriptions.

Known limitations of the current run:

- BAML prints richer prompt/rendering logs by default, while the direct OpenAI runners store more raw response metadata in JSON.
- The expected labels are useful review targets, but some support-ticket labels are subjective.
- The benchmark measures this workflow, not every BAML use case.

Use the current results to evaluate BAML's developer workflow, schema reliability, generated client, and testing ergonomics. Do not treat the strict all-label score as a standalone product-quality score.
