from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from .io_utils import COMPARISON_DIR, DOCS_DIR, RAW_DIR, ensure_output_dirs, load_tickets, read_json

IMPLEMENTATIONS = ["baml", "openai_structured", "openai_json"]
STEPS = ["classification", "facts", "draft"]
LABEL_FIELDS = [
    ("category", "expected_category"),
    ("urgency", "expected_urgency"),
    ("team", "expected_team"),
    ("needs_human_review", "expected_needs_human_review"),
]


def normalize_label(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        value = value.value
    text = str(value).strip().split(".")[-1]
    return text.lower().replace("-", "_")


def generate_comparison() -> None:
    ensure_output_dirs()
    tickets = {ticket.ticket_id: ticket for ticket in load_tickets()}
    rows = []
    latency_rows = []

    for implementation in IMPLEMENTATIONS:
        impl_dir = RAW_DIR / implementation
        if not impl_dir.exists():
            continue
        for path in sorted(impl_dir.glob("*/run_*.json")):
            run = read_json(path)
            ticket = tickets[run["ticket_id"]]
            classification = run.get("steps", {}).get("classification", {})
            parsed = classification.get("parsed") or {}
            schema_success = all((run.get("steps", {}).get(step, {}).get("ok") is True) for step in STEPS)

            row = {
                "implementation": implementation,
                "ticket_id": ticket.ticket_id,
                "scenario": ticket.scenario,
                "run_index": run["run_index"],
                "schema_success": int(schema_success),
            }
            label_matches = []
            for actual_field, expected_field in LABEL_FIELDS:
                actual = parsed.get(actual_field)
                expected = getattr(ticket, expected_field)
                match = normalize_label(actual) == normalize_label(expected)
                row[f"{actual_field}_actual"] = normalize_label(actual)
                row[f"{actual_field}_expected"] = normalize_label(expected)
                row[f"{actual_field}_match"] = int(match)
                label_matches.append(match)
            row["all_expected_labels_match"] = int(all(label_matches))
            row["end_to_end_success"] = int(schema_success and all(label_matches))
            rows.append(row)

            for step_name, step in run.get("steps", {}).items():
                latency = step.get("latency_ms")
                if latency is not None:
                    latency_rows.append(
                        {
                            "implementation": implementation,
                            "ticket_id": ticket.ticket_id,
                            "run_index": run["run_index"],
                            "step": step_name,
                            "latency_ms": latency,
                        }
                    )

    _write_csv(COMPARISON_DIR / "run_level_results.csv", rows)
    _write_csv(COMPARISON_DIR / "latency_by_run_step.csv", latency_rows)
    _write_csv(COMPARISON_DIR / "metrics_by_implementation.csv", _metrics_by_implementation(rows))
    _write_csv(COMPARISON_DIR / "latency_by_step.csv", _latency_by_step(latency_rows))
    workflow_rows = _workflow_by_ticket(rows)
    _write_csv(COMPARISON_DIR / "workflow_by_ticket.csv", workflow_rows)
    _write_csv(COMPARISON_DIR / "manual_failure_counts.csv", _manual_failure_counts())
    _write_markdown_summary(rows)
    _write_ticket_markdown_summary(workflow_rows)


def _metrics_by_implementation(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["implementation"]].append(row)

    metrics = []
    for implementation, items in grouped.items():
        count = len(items)
        if count == 0:
            continue
        metrics.append(
            {
                "implementation": implementation,
                "runs": count,
                "schema_success_rate": _avg(items, "schema_success"),
                "category_accuracy": _avg(items, "category_match"),
                "urgency_accuracy": _avg(items, "urgency_match"),
                "team_accuracy": _avg(items, "team_match"),
                "human_review_accuracy": _avg(items, "needs_human_review_match"),
                "all_label_accuracy": _avg(items, "all_expected_labels_match"),
                "end_to_end_success_rate": _avg(items, "end_to_end_success"),
            }
        )
    return metrics


def _latency_by_step(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(row["implementation"], row["step"])].append(float(row["latency_ms"]))

    summary = []
    for (implementation, step), values in grouped.items():
        values = sorted(values)
        p95_index = max(0, min(len(values) - 1, int(round(0.95 * (len(values) - 1)))))
        summary.append(
            {
                "implementation": implementation,
                "step": step,
                "calls": len(values),
                "median_latency_ms": median(values),
                "p95_latency_ms": values[p95_index],
            }
        )
    return summary


def _workflow_by_ticket(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["implementation"], row["ticket_id"], row["scenario"])].append(row)

    summary = []
    for (implementation, ticket_id, scenario), items in grouped.items():
        summary.append(
            {
                "implementation": implementation,
                "ticket_id": ticket_id,
                "scenario": scenario,
                "runs": len(items),
                "end_to_end_success_rate": _avg(items, "end_to_end_success"),
                "all_label_accuracy": _avg(items, "all_expected_labels_match"),
                "average_label_match_rate": sum(
                    _avg(items, field)
                    for field in [
                        "category_match",
                        "urgency_match",
                        "team_match",
                        "needs_human_review_match",
                    ]
                )
                / 4,
            }
        )
    return summary


def _manual_failure_counts() -> list[dict[str, Any]]:
    path = DOCS_DIR / "manual_review.csv"
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    failure_fields = [
        "hallucinated_fact",
        "unsafe_draft",
        "missed_escalation",
        "wrong_routing",
        "ambiguity_over_assumed",
    ]
    grouped: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        implementation = row.get("implementation", "").strip()
        if not implementation:
            continue
        for field in failure_fields:
            value = row.get(field, "").strip().lower()
            if value in {"1", "true", "yes", "y"}:
                grouped[(implementation, field)] += 1

    return [
        {"implementation": implementation, "failure_type": field, "count": count}
        for (implementation, field), count in sorted(grouped.items())
    ]


def _avg(rows: list[dict[str, Any]], field: str) -> float:
    return sum(float(row[field]) for row in rows) / len(rows)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown_summary(rows: list[dict[str, Any]]) -> None:
    metrics = _metrics_by_implementation(rows)
    path = COMPARISON_DIR / "results_table.md"
    if not metrics:
        path.write_text("# Results\n\nNo benchmark outputs found yet. Run the benchmark first.\n")
        return

    display_name = {
        "baml": "BAML",
        "openai_structured": "OpenAI Structured Output",
        "openai_json": "OpenAI JSON Prompt",
    }
    lines = [
        "# Benchmark Results",
        "",
        "## Summary by Implementation",
        "",
        "| Implementation | Runs | Schema-valid workflows | Category matched | Urgency matched | Routing team matched | Human-review flag matched | Strict all-label match |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in metrics:
        lines.append(
            f"| {display_name.get(row['implementation'], row['implementation'])} | {row['runs']} | "
            f"{row['schema_success_rate']:.2%} | {row['category_accuracy']:.2%} | "
            f"{row['urgency_accuracy']:.2%} | {row['team_accuracy']:.2%} | "
            f"{row['human_review_accuracy']:.2%} | {row['all_label_accuracy']:.2%} |"
        )
    lines.append("")
    lines.append(
        "Note: strict all-label match requires category, urgency, routing team, and human-review flag to all match the locked expected labels in the same run."
    )
    lines.append(
        "Use this as a diligence benchmark, not a definitive leaderboard: the current run is best for comparing developer workflow, schema reliability, and review ergonomics."
    )
    lines.append("")
    path.write_text("\n".join(lines))


def _write_ticket_markdown_summary(rows: list[dict[str, Any]]) -> None:
    path = COMPARISON_DIR / "ticket_results_table.md"
    if not rows:
        path.write_text("# Ticket-Level Results\n\nNo benchmark outputs found yet. Run the benchmark first.\n")
        return

    display_name = {
        "baml": "BAML",
        "openai_structured": "OpenAI Structured Output",
        "openai_json": "OpenAI JSON Prompt",
    }
    scenario_name = {
        "clean_product_bug": "Clean product bug",
        "enterprise_outage_renewal_pressure": "Enterprise outage with renewal pressure",
        "vague_complaint_missing_info": "Vague complaint with missing information",
        "billing_dispute": "Billing dispute",
        "security_report": "Security report",
        "feature_request": "Feature request",
        "data_loss_concern": "Data loss concern",
        "integration_failure": "Integration failure",
        "performance_degradation": "Performance degradation",
        "account_access_issue": "Account access issue",
        "compliance_privacy_concern": "Compliance and privacy concern",
        "low_priority_how_to": "Low-priority how-to question",
    }

    lines = [
        "# Ticket-Level Results",
        "",
        "| Ticket | Scenario | Implementation | Average label match | Strict all-label match |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    implementation_order = {"baml": 0, "openai_structured": 1, "openai_json": 2}
    for row in sorted(rows, key=lambda item: (item["ticket_id"], implementation_order.get(item["implementation"], 99))):
        lines.append(
            f"| {row['ticket_id']} | {scenario_name.get(row['scenario'], row['scenario'])} | "
            f"{display_name.get(row['implementation'], row['implementation'])} | "
            f"{float(row.get('average_label_match_rate', row['all_label_accuracy'])):.2%} | "
            f"{float(row['all_label_accuracy']):.2%} |"
        )
    lines.append("")
    lines.append(
        "Average label match is the mean of category, urgency, routing team, and human-review flag match rates. Strict all-label match requires all four labels to match in the same run."
    )
    lines.append("")
    path.write_text("\n".join(lines))
