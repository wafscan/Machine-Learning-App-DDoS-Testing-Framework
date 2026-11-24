"""Offline synthetic application-traffic event generator."""

from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List


PATHS = ["/", "/login", "/search", "/products", "/api/items", "/account"]
METHODS = ["GET", "GET", "GET", "POST"]
UA_FAMILIES = ["Browser-A", "Browser-B", "Mobile-App", "Automation-Test"]


def parse_start(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def generate_events(
    scenario: str,
    count: int,
    start: datetime,
    rng: random.Random,
) -> List[Dict]:
    events: List[Dict] = []
    client_last_seen: Dict[str, datetime] = {}

    if scenario == "client_concentration":
        clients = [f"synthetic-client-{i:03d}" for i in range(3)]
    elif scenario == "rate_deviation":
        clients = [f"synthetic-client-{i:03d}" for i in range(12)]
    else:
        clients = [f"synthetic-client-{i:03d}" for i in range(20)]

    for index in range(count):
        client = rng.choice(clients)

        if scenario == "path_concentration":
            path = rng.choice(["/login", "/api/items"])
        else:
            path = rng.choice(PATHS)

        if scenario == "user_agent_shift":
            ua = rng.choice(["Automation-Test", "Automation-Test", "Browser-A"])
        else:
            ua = rng.choice(UA_FAMILIES)

        if scenario == "rate_deviation":
            interval_ms = rng.randint(100, 450)
        else:
            interval_ms = rng.randint(1500, 9000)

        previous = client_last_seen.get(client, start)
        timestamp = previous + timedelta(milliseconds=interval_ms)
        client_last_seen[client] = timestamp

        event = {
            "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
            "scenario": scenario,
            "label": "normal" if scenario == "baseline" else "behavioral_deviation",
            "client_id": client,
            "method": rng.choice(METHODS),
            "path": path,
            "user_agent_family": ua,
            "status_code": rng.choice([200, 200, 200, 304]),
            "response_bytes": rng.randint(500, 12000),
            "inter_arrival_ms": interval_ms,
        }
        events.append(event)

    return events


def write_outputs(events: Iterable[Dict], output_dir: Path) -> Dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    events = list(events)

    jsonl_path = output_dir / "events.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    csv_path = output_dir / "events.csv"
    if events:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(events[0].keys()))
            writer.writeheader()
            writer.writerows(events)

    by_scenario: Dict[str, int] = {}
    by_label: Dict[str, int] = {}
    for event in events:
        by_scenario[event["scenario"]] = by_scenario.get(event["scenario"], 0) + 1
        by_label[event["label"]] = by_label.get(event["label"], 0) + 1

    summary = {
        "total_events": len(events),
        "scenario_counts": by_scenario,
        "label_counts": by_label,
        "unique_synthetic_clients": len({e["client_id"] for e in events}),
        "unique_paths": len({e["path"] for e in events}),
        "note": "Offline synthetic data only; no network requests were sent."
    }

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
