# Ticket-Level Results

| Ticket | Scenario | Implementation | Average label match | Strict all-label match |
| --- | --- | --- | ---: | ---: |
| T001 | Clean product bug | BAML | 70.00% | 20.00% |
| T001 | Clean product bug | OpenAI JSON Prompt | 50.00% | 0.00% |
| T001 | Clean product bug | OpenAI Structured Output | 70.00% | 0.00% |
| T002 | Enterprise outage with renewal pressure | BAML | 50.00% | 0.00% |
| T002 | Enterprise outage with renewal pressure | OpenAI JSON Prompt | 75.00% | 0.00% |
| T002 | Enterprise outage with renewal pressure | OpenAI Structured Output | 75.00% | 0.00% |
| T003 | Vague complaint with missing information | BAML | 50.00% | 0.00% |
| T003 | Vague complaint with missing information | OpenAI JSON Prompt | 50.00% | 0.00% |
| T003 | Vague complaint with missing information | OpenAI Structured Output | 30.00% | 0.00% |
| T004 | Billing dispute | BAML | 75.00% | 0.00% |
| T004 | Billing dispute | OpenAI JSON Prompt | 100.00% | 100.00% |
| T004 | Billing dispute | OpenAI Structured Output | 100.00% | 100.00% |
| T005 | Security report | BAML | 75.00% | 0.00% |
| T005 | Security report | OpenAI JSON Prompt | 85.00% | 40.00% |
| T005 | Security report | OpenAI Structured Output | 100.00% | 100.00% |
| T006 | Feature request | BAML | 75.00% | 0.00% |
| T006 | Feature request | OpenAI JSON Prompt | 65.00% | 0.00% |
| T006 | Feature request | OpenAI Structured Output | 100.00% | 100.00% |
| T007 | Data loss concern | BAML | 75.00% | 0.00% |
| T007 | Data loss concern | OpenAI JSON Prompt | 95.00% | 80.00% |
| T007 | Data loss concern | OpenAI Structured Output | 100.00% | 100.00% |
| T008 | Integration failure | BAML | 75.00% | 0.00% |
| T008 | Integration failure | OpenAI JSON Prompt | 100.00% | 100.00% |
| T008 | Integration failure | OpenAI Structured Output | 95.00% | 80.00% |
| T009 | Performance degradation | BAML | 50.00% | 0.00% |
| T009 | Performance degradation | OpenAI JSON Prompt | 100.00% | 100.00% |
| T009 | Performance degradation | OpenAI Structured Output | 75.00% | 0.00% |
| T010 | Account access issue | BAML | 70.00% | 40.00% |
| T010 | Account access issue | OpenAI JSON Prompt | 50.00% | 0.00% |
| T010 | Account access issue | OpenAI Structured Output | 55.00% | 0.00% |
| T011 | Compliance and privacy concern | BAML | 75.00% | 0.00% |
| T011 | Compliance and privacy concern | OpenAI JSON Prompt | 75.00% | 0.00% |
| T011 | Compliance and privacy concern | OpenAI Structured Output | 75.00% | 0.00% |
| T012 | Low-priority how-to question | BAML | 100.00% | 100.00% |
| T012 | Low-priority how-to question | OpenAI JSON Prompt | 100.00% | 100.00% |
| T012 | Low-priority how-to question | OpenAI Structured Output | 95.00% | 80.00% |

Average label match is the mean of category, urgency, routing team, and human-review flag match rates. Strict all-label match requires all four labels to match in the same run.
