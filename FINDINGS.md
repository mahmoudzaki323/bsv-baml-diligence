# BAML Diligence Findings

## Diligence question

Does BAML make structured LLM application logic easier to define, test, debug, and evolve than direct Gemini SDK implementations?

## Setup notes

- BAML docs used: https://docs.boundaryml.com
- Gemini SDK docs used: Google Gen AI Python SDK docs via Context7.
- Local setup command planned: `uv sync`
- BAML generation command planned: `uv run baml-cli generate`

Fill in during hands-on testing:

- Time to first successful BAML function call:
- Main install/setup friction:
- Most useful docs page:
- Confusing docs or missing mental model:
- CLI/codegen issues:

## Benchmark notes

- Model used:
- Date run:
- Smoke test result:
- Full benchmark result:
- Any API/model limitations:

## Manual review observations

Fill this after reviewing outputs and updating `docs/manual_review.csv`.

- Where BAML performed best:
- Where BAML failed or was awkward:
- Where Gemini structured baseline performed best:
- Where plain JSON baseline failed or surprised me:
- Most important hallucination or safety issue:
- Most important routing/classification issue:

## Strategic assessment draft

BAML is most compelling if teams have many production LLM calls that need shared schemas, typed contracts, testing, prompt iteration, and code review. It is less compelling for a single one-off prompt where the DSL and generation workflow can feel like extra ceremony.

Open diligence questions:

- Does BAML become the workflow layer for teams with dozens or hundreds of LLM calls?
- Is the DSL adoption cost justified versus native provider structured-output APIs?
- Can BAML maintain differentiation as Gemini, OpenAI, Anthropic, LangChain, Instructor, and framework tooling improve?
- Does the generated-client workflow fit naturally into existing CI/code-review processes?

## Bottom-line placeholder

Final judgment goes here after the benchmark and manual review are complete.
