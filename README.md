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
2. `openai_structured`: Direct OpenAI Chat Completions call with `json_schema` structured output from the same Pydantic schema.
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
PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli report
```

Outputs are written to:

- `outputs/raw/`: raw per-run outputs.
- `outputs/comparison/`: computed CSVs and markdown results table.
- `artifacts/charts/`: charts generated from actual benchmark results.

## Manual review

Automated metrics are not enough for this diligence. Review the outputs and fill `docs/manual_review.csv` using `docs/scoring_rubric.md`.

Then regenerate the report:

```bash
PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli report
```

## Charts

Charts are generated only from observed results, not arbitrary subjective scores:

- `schema_success_rate.png`
- `expected_label_accuracy.png`
- `latency_by_step.png`
- `manual_failure_counts.png`
- `label_match_by_ticket.png`
- `workflow_success_by_ticket.png` is kept as a compatibility filename, but now shows average expected-label match rather than a brittle all-or-nothing workflow score.

## Notes for the final writeup

Use `FINDINGS.md` for running notes. Use `docs/google_doc_outline.md` as the Google Doc structure.
