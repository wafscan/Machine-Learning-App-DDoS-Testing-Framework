#!/usr/bin/env python3
"""Generate offline synthetic application-behavior events."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from simulator import generate_events, parse_start, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate offline synthetic application DDoS-behavior test data."
    )
    parser.add_argument(
        "--config",
        default="config/test_config.json",
        help="Path to JSON configuration (default: config/test_config.json)",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_file():
        parser.error(f"Configuration file not found: {config_path}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    count = int(config.get("events_per_scenario", 250))
    if count < 1 or count > 100000:
        parser.error("events_per_scenario must be between 1 and 100000")

    scenarios = config.get("scenarios", ["baseline"])
    allowed = {
        "baseline",
        "rate_deviation",
        "client_concentration",
        "path_concentration",
        "user_agent_shift",
    }
    unknown = set(scenarios) - allowed
    if unknown:
        parser.error(f"Unknown scenarios: {', '.join(sorted(unknown))}")

    rng = random.Random(int(config.get("seed", 42)))
    start = parse_start(config.get("start_time_utc", "2026-01-01T12:00:00Z"))

    all_events = []
    for scenario in scenarios:
        all_events.extend(generate_events(scenario, count, start, rng))

    output_dir = Path(config.get("output_directory", "output"))
    summary = write_outputs(all_events, output_dir)

    print("Machine Learning App DDoS Testing Framework")
    print("Mode: offline synthetic simulation")
    print(f"Events generated: {summary['total_events']}")
    print(f"Output directory: {output_dir}")
    print("No network traffic was sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
