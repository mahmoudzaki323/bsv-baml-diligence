# Benchmark Results

## Summary by Implementation

| Implementation | Runs | Schema-valid workflows | Category matched | Urgency matched | Routing team matched | Human-review flag matched | Strict all-label match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BAML | 60 | 100.00% | 88.33% | 26.67% | 78.33% | 86.67% | 13.33% |
| OpenAI Structured Output | 60 | 100.00% | 83.33% | 66.67% | 91.67% | 81.67% | 46.67% |
| OpenAI JSON Prompt | 60 | 100.00% | 90.00% | 60.00% | 85.00% | 80.00% | 43.33% |

Note: strict all-label match requires category, urgency, routing team, and human-review flag to all match the locked expected labels in the same run.
