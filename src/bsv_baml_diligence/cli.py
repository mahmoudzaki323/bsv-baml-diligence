from __future__ import annotations

import argparse

from .charts import generate_charts
from .compare import generate_comparison
from .run_all import RUNNERS, run_all


def main() -> None:
    parser = argparse.ArgumentParser(description="BSV BAML diligence benchmark")
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke = subparsers.add_parser("smoke", help="Run 1 ticket once across implementations")
    smoke.add_argument("--force", action="store_true", help="Overwrite cached outputs")
    smoke.add_argument("--implementation", choices=list(RUNNERS), action="append", help="Limit to one implementation; repeatable")

    benchmark = subparsers.add_parser("benchmark", help="Run the full or partial benchmark")
    benchmark.add_argument("--runs", type=int, default=5)
    benchmark.add_argument("--ticket-limit", type=int, default=None)
    benchmark.add_argument("--force", action="store_true", help="Overwrite cached outputs")
    benchmark.add_argument("--implementation", choices=list(RUNNERS), action="append", help="Limit to one implementation; repeatable")

    subparsers.add_parser("compare", help="Generate comparison CSVs and markdown tables")
    subparsers.add_parser("charts", help="Generate charts from comparison CSVs")
    subparsers.add_parser("report", help="Generate comparison tables and charts")

    args = parser.parse_args()

    if args.command == "smoke":
        run_all(runs=1, ticket_limit=1, force=args.force, implementations=args.implementation)
    elif args.command == "benchmark":
        run_all(runs=args.runs, ticket_limit=args.ticket_limit, force=args.force, implementations=args.implementation)
    elif args.command == "compare":
        generate_comparison()
    elif args.command == "charts":
        generate_charts()
    elif args.command == "report":
        generate_comparison()
        generate_charts()
