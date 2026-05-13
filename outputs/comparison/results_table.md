# Benchmark Results

## Summary by Implementation

| Implementation | Runs | Schema-valid workflows | Category matched | Urgency matched | Routing team matched | Human-review flag matched | Strict all-label match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BAML | 60 | 98.33% | 90.00% | 25.00% | 76.67% | 83.33% | 10.00% |
| OpenAI Structured Output | 60 | 100.00% | 88.33% | 63.33% | 90.00% | 85.00% | 46.67% |
| OpenAI JSON Prompt | 60 | 100.00% | 90.00% | 60.00% | 86.67% | 75.00% | 40.00% |

Note: strict all-label match requires category, urgency, routing team, and human-review flag to all match the locked expected labels in the same run.
Use this as a diligence benchmark, not a definitive leaderboard: the current run is best for comparing developer workflow, schema reliability, and review ergonomics.
