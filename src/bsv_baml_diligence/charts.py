from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from .io_utils import CHARTS_DIR, COMPARISON_DIR, ensure_output_dirs

IMPLEMENTATION_LABELS = {
    "baml": "BAML",
    "openai_structured": "OpenAI Structured Output",
    "openai_json": "OpenAI JSON Prompt",
}

FIELD_LABELS = {
    "category_accuracy": "Category",
    "urgency_accuracy": "Urgency",
    "team_accuracy": "Routing team",
    "human_review_accuracy": "Human-review flag",
}

STEP_LABELS = {
    "classification": "Classify ticket",
    "facts": "Extract facts",
    "draft": "Draft response",
}

SCENARIO_LABELS = {
    "clean_product_bug": "Clean bug",
    "enterprise_outage_renewal_pressure": "Enterprise outage",
    "vague_complaint_missing_info": "Vague complaint",
    "billing_dispute": "Billing dispute",
    "security_report": "Security report",
    "feature_request": "Feature request",
    "data_loss_concern": "Data loss concern",
    "integration_failure": "Integration failure",
    "performance_degradation": "Performance issue",
    "account_access_issue": "Account access",
    "compliance_privacy_concern": "Compliance/privacy",
    "low_priority_how_to": "How-to question",
}


def generate_charts() -> None:
    ensure_output_dirs()
    _schema_success_chart()
    _expected_label_accuracy_chart()
    _latency_chart()
    _manual_failure_chart()
    _label_match_by_ticket_chart()


def _read_csv(name: str) -> pd.DataFrame:
    path = COMPARISON_DIR / name
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def _save(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def _add_bar_labels(ax, *, percent: bool = False, decimals: int = 0) -> None:
    for container in ax.containers:
        labels = []
        for value in container.datavalues:
            if pd.isna(value):
                labels.append("")
            elif percent:
                labels.append(f"{value:.{decimals}%}")
            else:
                labels.append(f"{value:.{decimals}f}")
        ax.bar_label(container, labels=labels, padding=3, fontsize=8)


def _implementation_order(df: pd.DataFrame) -> list[str]:
    preferred = ["baml", "openai_structured", "openai_json"]
    return [item for item in preferred if item in set(df["implementation"])]


def _schema_success_chart() -> None:
    df = _read_csv("metrics_by_implementation.csv")
    if df.empty:
        return
    df = df.set_index("implementation").loc[_implementation_order(df)].reset_index()
    df["Implementation"] = df["implementation"].map(IMPLEMENTATION_LABELS)
    ax = df.plot.bar(x="Implementation", y="schema_success_rate", legend=False, ylim=(0, 1.12), color="#2F6F73")
    ax.set_title("Schema-valid workflows by implementation\nAll three workflow steps returned valid structured data")
    ax.set_xlabel("Implementation")
    ax.set_ylabel("Share of runs with all three steps schema-valid")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    _add_bar_labels(ax, percent=True)
    _save(CHARTS_DIR / "schema_success_rate.png")


def _expected_label_accuracy_chart() -> None:
    df = _read_csv("metrics_by_implementation.csv")
    if df.empty:
        return
    df = df.set_index("implementation").loc[_implementation_order(df)]
    df.index = [IMPLEMENTATION_LABELS[item] for item in df.index]
    chart_df = df[list(FIELD_LABELS)].rename(columns=FIELD_LABELS)
    ax = chart_df.plot.bar(ylim=(0, 1.18), figsize=(11, 5.5))
    ax.set_title("Expected-label match rate by field\nLocked labels are review targets, not absolute ground truth")
    ax.set_xlabel("Implementation")
    ax.set_ylabel("Share of runs matching locked expected label")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.legend(title="Field evaluated")
    _add_bar_labels(ax, percent=True)
    _save(CHARTS_DIR / "expected_label_accuracy.png")


def _latency_chart() -> None:
    df = _read_csv("latency_by_step.csv")
    if df.empty:
        return
    df["Implementation"] = df["implementation"].map(IMPLEMENTATION_LABELS)
    df["Workflow step"] = df["step"].map(STEP_LABELS)
    df["Median latency (seconds)"] = df["median_latency_ms"] / 1000
    pivot = df.pivot(index="Workflow step", columns="Implementation", values="Median latency (seconds)")
    pivot = pivot.loc[[label for label in STEP_LABELS.values() if label in pivot.index]]
    ax = pivot.plot.bar(figsize=(11, 5.5))
    ax.set_title("Median API latency by workflow step\nLower is better; each bar summarizes observed benchmark calls")
    ax.set_xlabel("Workflow step")
    ax.set_ylabel("Median latency in seconds")
    ax.legend(title="Implementation")
    _add_bar_labels(ax, decimals=1)
    _save(CHARTS_DIR / "latency_by_step.png")


def _manual_failure_chart() -> None:
    df = _read_csv("manual_failure_counts.csv")
    if df.empty:
        return
    df["Implementation"] = df["implementation"].map(IMPLEMENTATION_LABELS)
    df["Failure type"] = df["failure_type"].str.replace("_", " ").str.title()
    pivot = df.pivot(index="Failure type", columns="Implementation", values="count").fillna(0)
    ax = pivot.plot.bar(figsize=(10, 5))
    ax.set_title("Manual review failure counts\nGenerated only after manual review is completed")
    ax.set_xlabel("Failure type")
    ax.set_ylabel("Number of flagged runs")
    ax.legend(title="Implementation")
    _add_bar_labels(ax)
    _save(CHARTS_DIR / "manual_failure_counts.png")


def _label_match_by_ticket_chart() -> None:
    df = _read_csv("workflow_by_ticket.csv")
    if df.empty:
        return
    value_column = "average_label_match_rate" if "average_label_match_rate" in df.columns else "all_label_accuracy"
    df["Implementation"] = df["implementation"].map(IMPLEMENTATION_LABELS)
    df["Ticket scenario"] = df["scenario"].map(SCENARIO_LABELS).fillna(df["ticket_id"])
    pivot = df.pivot_table(index="Ticket scenario", columns="Implementation", values=value_column, aggfunc="mean")
    ordered_labels = [label for label in SCENARIO_LABELS.values() if label in pivot.index]
    pivot = pivot.loc[ordered_labels]
    ax = pivot.plot.bar(figsize=(14, 6.5), ylim=(0, 1.16))
    ax.set_title("Average expected-label match by ticket\nMean of category, urgency, routing team, and human-review match rates")
    ax.set_xlabel("Ticket scenario")
    ax.set_ylabel("Average share of labels matched")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.legend(title="Implementation")
    _add_bar_labels(ax, percent=True)
    _save(CHARTS_DIR / "label_match_by_ticket.png")
