# BAML Developer Tools Diligence

This repo contains a small hands-on benchmark of [BAML](https://www.boundaryml.com/) for a production-style LLM workflow.

The question I wanted to test was simple:

> Does BAML make structured LLM workflows easier to define, run, and maintain than direct API calls?

## What I built

I built a support-ticket triage workflow using 12 synthetic B2B SaaS support tickets.

For each ticket, the model had to:

1. Classify the issue.
2. Decide urgency.
3. Choose who should handle it.
4. Decide whether a human should review it.
5. Extract the important facts.
6. Draft a safe support response.

I tested the same workflow three ways:

| Version | What it means |
| --- | --- |
| BAML | BAML typed functions and generated Python client |
| OpenAI Structured Output | Direct OpenAI API with strict structured output |
| OpenAI JSON Prompt | Plain JSON prompt plus Python validation |

All three used the same model: `gpt-5.4-nano`.

## Main results

| Implementation | Valid structured workflows | Category match | Urgency match | Assigned-team match | Human-review match |
| --- | ---: | ---: | ---: | ---: | ---: |
| BAML | 98.33% | 90.00% | 25.00% | 76.67% | 83.33% |
| OpenAI Structured Output | 100.00% | 88.33% | 63.33% | 90.00% | 85.00% |
| OpenAI JSON Prompt | 100.00% | 90.00% | 60.00% | 86.67% | 75.00% |

Short interpretation:

- BAML worked and was clean to organize.
- BAML did not automatically improve model judgment.
- The weakest metric was urgency, partly because my urgency rubric was not strict enough.
- BAML had one failed run where the model chose an option outside the allowed list. BAML caught it and stopped the workflow.
- For simple workflows, direct API calls may be enough. BAML is more interesting when a team has many LLM calls to maintain.

## Where to look

| Path | What it contains |
| --- | --- |
| `data/tickets.json` | The 12 synthetic support tickets and expected labels |
| `baml_src/` | BAML function and type definitions |
| `src/bsv_baml_diligence/` | Python benchmark code |
| `outputs/raw/` | Raw outputs from all 180 runs |
| `outputs/comparison/results_table.md` | Main results table |
| `outputs/comparison/ticket_results_table.md` | Ticket-level results |
| `artifacts/charts/` | Generated charts |
| `docs/scoring_rubric.md` | Manual-review rubric |

## Charts

Generated charts are in `artifacts/charts/`:

- `schema_success_rate.png`
- `expected_label_accuracy.png`
- `latency_by_step.png`
- `label_match_by_ticket.png`

These charts use actual benchmark results, not manual scoring.

## Reproduce the benchmark

Install dependencies:

```bash
uv sync
```

Create a local `.env` file:

```bash
cp .env.example .env
```

Add your OpenAI key:

```bash
OPENAI_API_KEY=your_key_here
BENCHMARK_MODEL=gpt-5.4-nano
```

Generate the BAML client:

```bash
uv run baml-cli generate
```

Run a smoke test:

```bash
PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli smoke --force
```

Run the full benchmark:

```bash
PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli benchmark --runs 5 --force
```

Regenerate tables and charts:

```bash
MPLBACKEND=Agg PYDANTIC_DISABLE_PLUGINS=1 PYTHONPATH=src ./.venv/bin/python -m bsv_baml_diligence.cli report
```

## Notes

This is a diligence artifact, not a definitive leaderboard. The goal was to evaluate setup, usability, structure, and workflow fit.

The raw outputs are included so the results can be inspected without rerunning the API calls.

## Follow-up experiments

If I had more time, I would run four follow-up tests:

1. Tighten the urgency rubric and rerun the benchmark. Urgency was the weakest metric, and some tickets could reasonably fit more than one severity level.
2. Add automatic retry handling. One BAML run failed because the model chose an option outside the allowed list; a production workflow should ask the model to try again instead of stopping.
3. Test a larger workflow. BAML is most useful when there are many LLM calls, so I would test a workflow with more steps, shared functions, and prompt changes over time.
4. Add manual review scoring. The current charts measure structure and label matching, but a human should also review drafts for unsafe promises, unsupported facts, and missed escalation signals.

These follow-ups would better test whether BAML becomes more valuable as workflows get larger and harder to maintain.
