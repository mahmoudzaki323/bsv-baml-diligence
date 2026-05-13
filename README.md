# BSV BAML Diligence Benchmark

This repo contains a hands-on evaluation of BAML for production-style structured LLM workflows using the Gemini Developer API.

## Diligence question

Does BAML make structured LLM application logic easier to define, test, debug, and evolve than direct Gemini SDK implementations?

## What this benchmark builds

A three-step support ticket triage workflow:

1. Classify ticket category, urgency, team, and human-review requirement.
2. Extract grounded facts, missing information, customer impact, and risk signals.
3. Draft a safe customer-facing support response.

The same workflow is implemented three ways:

1. `baml`: BAML typed functions using the `google-ai` provider.
2. `gemini_structured`: Direct Gemini REST call with `responseJsonSchema` from the same Pydantic schema.
3. `gemini_json`: Direct Gemini REST call with plain JSON prompting and manual Pydantic validation.

## Why this is a useful BAML test

The goal is not to prove that BAML makes Gemini smarter. The goal is to test whether BAML improves the developer workflow once LLM calls become typed, multi-step application logic with expected labels, regression cases, and safety constraints.

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env`:

```bash
GOOGLE_API_KEY=your_key_here
BENCHMARK_MODEL=gemini-3-flash-preview
```

If you prefer Google docs' `GEMINI_API_KEY` name, also set `GOOGLE_API_KEY` to the same value because BAML's `google-ai` provider expects `GOOGLE_API_KEY`.

The direct REST baselines are used because this local environment hung while importing `google-genai`; the benchmark still uses the official Gemini `generateContent` API.

Generate the BAML Python client:

```bash
uv run baml-cli generate
```

If your installed BAML CLI exposes `baml generate` instead, use that equivalent command.

## Run

Smoke test one ticket once across all implementations:

```bash
PYTHONPATH=src uv run python -m bsv_baml_diligence.cli smoke --force
```

Full benchmark, matching the diligence plan:

```bash
PYTHONPATH=src uv run python -m bsv_baml_diligence.cli benchmark --runs 5 --force
```

Generate comparison tables and charts:

```bash
PYTHONPATH=src uv run python -m bsv_baml_diligence.cli report
```

Outputs are written to:

- `outputs/raw/`: raw per-run outputs.
- `outputs/comparison/`: computed CSVs and markdown results table.
- `artifacts/charts/`: charts generated from actual benchmark results.

## Manual review

Automated metrics are not enough for this diligence. Review the outputs and fill `docs/manual_review.csv` using `docs/scoring_rubric.md`.

Then regenerate the report:

```bash
PYTHONPATH=src uv run python -m bsv_baml_diligence.cli report
```

## Charts

Charts are generated only from observed results, not arbitrary subjective scores:

- `schema_success_rate.png`
- `expected_label_accuracy.png`
- `latency_by_step.png`
- `manual_failure_counts.png`
- `workflow_success_by_ticket.png`

## Notes for the final writeup

Use `FINDINGS.md` for running notes. Use `docs/google_doc_outline.md` as the Google Doc structure.
