# BAML Diligence Findings

## Diligence question

Does BAML make structured LLM application logic easier to define, test, debug, and evolve than direct OpenAI API implementations?

## Setup notes

- BAML docs used: https://docs.boundaryml.com
- OpenAI API docs used: https://developers.openai.com/api/docs
- Local setup command: `uv sync`
- BAML generation command: `uv run baml-cli generate`
- Model used: `gpt-5.4-nano`

Hands-on notes to refine after manual review:

- BAML setup required the normal define `.baml` files -> generate `baml_client` -> import generated client loop.
- The generated client worked cleanly after provider config was switched to OpenAI.
- The local Python environment mattered: Homebrew Python 3.13 avoided import stalls seen with the Anaconda Python venv.

## Benchmark results

Full benchmark completed with 12 tickets, 5 runs per ticket, 3 workflow steps, and 3 implementations.

| Implementation | Runs | Schema success | All expected labels | End-to-end success |
| --- | ---: | ---: | ---: | ---: |
| BAML | 60 | 100.00% | 13.33% | 13.33% |
| OpenAI structured baseline | 60 | 100.00% | 46.67% | 46.67% |
| OpenAI JSON baseline | 60 | 100.00% | 43.33% | 43.33% |

Detailed metrics:

| Implementation | Category | Urgency | Team | Human review |
| --- | ---: | ---: | ---: | ---: |
| BAML | 88.33% | 26.67% | 78.33% | 86.67% |
| OpenAI structured baseline | 83.33% | 66.67% | 91.67% | 81.67% |
| OpenAI JSON baseline | 90.00% | 60.00% | 85.00% | 80.00% |

Initial read:

- All three approaches produced schema-valid outputs across all runs.
- BAML's typed schema and generated client were reliable at parsing, but its prompt/schema rendering appeared to make urgency classification more aggressive than the locked expected labels.
- The direct structured baseline had the best exact-label and end-to-end performance in this test.
- The JSON baseline was close to structured output on labels, but it relies more on manual prompt/schema discipline in application code.

## Manual review observations

Fill this after reviewing outputs and updating `docs/manual_review.csv`.

- Where BAML performed best:
- Where BAML failed or was awkward:
- Where OpenAI structured baseline performed best:
- Where plain JSON baseline failed or surprised me:
- Most important hallucination or safety issue:
- Most important routing/classification issue:

## Strategic assessment draft

BAML is most compelling if teams have many production LLM calls that need shared schemas, typed contracts, testing, prompt iteration, and code review. It is less compelling for a single one-off prompt where the DSL and generation workflow can feel like extra ceremony.

Open diligence questions:

- Does BAML become the workflow layer for teams with dozens or hundreds of LLM calls?
- Is the DSL adoption cost justified versus native provider structured-output APIs?
- Can BAML maintain differentiation as OpenAI, Anthropic, LangChain, Instructor, and framework tooling improve?
- Does the generated-client workflow fit naturally into existing CI/code-review processes?

## Bottom-line placeholder

Final judgment goes here after manual review is complete.
