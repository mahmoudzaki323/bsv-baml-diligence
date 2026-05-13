from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from .io_utils import CHARTS_DIR, COMPARISON_DIR, ensure_output_dirs


def generate_charts() -> None:
    ensure_output_dirs()
    _schema_success_chart()
    _expected_label_accuracy_chart()
    _latency_chart()
    _manual_failure_chart()
    _workflow_by_ticket_chart()


def _read_csv(name: str) -> pd.DataFrame:
    path = COMPARISON_DIR / name
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def _save(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def _schema_success_chart() -> None:
    df = _read_csv("metrics_by_implementation.csv")
    if df.empty:
        return
    ax = df.plot.bar(x="implementation", y="schema_success_rate", legend=False, ylim=(0, 1), color="#2F6F73")
    ax.set_title("Schema success rate by implementation")
    ax.set_xlabel("")
    ax.set_ylabel("Success rate")
    _save(CHARTS_DIR / "schema_success_rate.png")


def _expected_label_accuracy_chart() -> None:
    df = _read_csv("metrics_by_implementation.csv")
    if df.empty:
        return
    cols = ["category_accuracy", "urgency_accuracy", "team_accuracy", "human_review_accuracy"]
    ax = df.set_index("implementation")[cols].plot.bar(ylim=(0, 1))
    ax.set_title("Expected-label accuracy by implementation")
    ax.set_xlabel("")
    ax.set_ylabel("Accuracy")
    _save(CHARTS_DIR / "expected_label_accuracy.png")


def _latency_chart() -> None:
    df = _read_csv("latency_by_step.csv")
    if df.empty:
        return
    pivot = df.pivot(index="step", columns="implementation", values="median_latency_ms")
    ax = pivot.plot.bar()
    ax.set_title("Median latency by workflow step")
    ax.set_xlabel("")
    ax.set_ylabel("Median latency, ms")
    _save(CHARTS_DIR / "latency_by_step.png")


def _manual_failure_chart() -> None:
    df = _read_csv("manual_failure_counts.csv")
    if df.empty:
        return
    pivot = df.pivot(index="failure_type", columns="implementation", values="count").fillna(0)
    ax = pivot.plot.bar()
    ax.set_title("Manual review failure counts")
    ax.set_xlabel("")
    ax.set_ylabel("Count")
    _save(CHARTS_DIR / "manual_failure_counts.png")


def _workflow_by_ticket_chart() -> None:
    df = _read_csv("workflow_by_ticket.csv")
    if df.empty:
        return
    pivot = df.pivot_table(index="ticket_id", columns="implementation", values="end_to_end_success_rate", aggfunc="mean")
    ax = pivot.plot.bar(figsize=(11, 5), ylim=(0, 1))
    ax.set_title("End-to-end success by ticket")
    ax.set_xlabel("Ticket")
    ax.set_ylabel("Success rate")
    _save(CHARTS_DIR / "workflow_success_by_ticket.png")
