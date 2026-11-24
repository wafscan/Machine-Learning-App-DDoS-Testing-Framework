# Machine Learning App DDoS Testing Framework

A vendor-neutral WAFscan project for evaluating application-layer behavioral detection and mitigation.

## Current release: 0.1.0

This first release is an **offline scenario simulator**. It creates labeled, synthetic application-request events and a summary report. It does not send traffic to a network target, spoof source addresses, or attempt to overwhelm a service.

This is intentional: it provides reproducible test data and a common scenario format before adding tightly controlled integrations for authorized test environments.

## Goals

- Describe behavioral test scenarios independently of a WAF vendor.
- Generate repeatable synthetic request-event datasets.
- Represent normal variation and suspicious behavioral deviations.
- Record scenario labels so detection outcomes can be evaluated.
- Keep configuration, scenarios, event generation, and reporting separate.

## Requirements

- Python 3.9+
- No third-party Python packages required

## Quick start

```bash
python3 src/run_simulation.py --config config/test_config.json
```

Output files are written to `output/`:
- `events.jsonl` — one synthetic request event per line
- `events.csv` — tabular version of the same events
- `summary.json` — scenario counts and basic distribution summary

You can change the scenario mix and event count in `config/test_config.json`.

## Included scenarios

| Scenario | Purpose |
|---|---|
| `baseline` | Ordinary application traffic with varied clients and paths |
| `rate_deviation` | Synthetic increase in request frequency for a subset of clients |
| `client_concentration` | Synthetic concentration of requests among fewer client identities |
| `path_concentration` | Synthetic concentration on a small set of application paths |
| `user_agent_shift` | Synthetic change in client-identification distribution |

All events are generated locally. The labels are ground truth for evaluating an analytics pipeline; they are not a claim that every unusual pattern is malicious.

## Event fields

- `timestamp`: ISO-8601 UTC timestamp
- `scenario`: scenario name
- `label`: `normal` or `behavioral_deviation`
- `client_id`: synthetic client identifier (not a real IP address)
- `method`: HTTP method label
- `path`: example application path
- `user_agent_family`: synthetic client family
- `status_code`: illustrative response code
- `response_bytes`: illustrative response size
- `inter_arrival_ms`: simulated time since the previous event for that client

## Interpreting results

This simulator creates test data; it does not train or validate a machine-learning model by itself. Feed the generated events into your own analytics or detection pipeline and compare its outputs with the `label` field.

Useful evaluation measures include:
- Detection rate / recall
- Precision
- False-positive rate
- Time to detection
- Mitigation decision and time to mitigation (when measured in an authorized lab)

Do not treat the synthetic labels as a universal definition of malicious traffic. Real application baselines and application context matter.

## Repository layout

```text
machine-learning-app-ddos-testing-framework/
├── README.md
├── LICENSE
├── .gitignore
├── config/
│   └── test_config.json
├── profiles/
│   └── scenarios.json
├── src/
│   ├── run_simulation.py
│   └── simulator.py
└── output/
    └── .gitkeep
```

## Roadmap

- **0.1.0:** Offline synthetic scenario generation and summary output.
- **0.2.0:** Pluggable event schema and import of sanitized application logs.
- **0.3.0:** Detection-result ingestion and precision/recall reporting.
- **Future:** Optional, rate-limited integrations for explicitly authorized lab environments, with hard duration/request limits and a prominent stop mechanism.

## Safety and authorization

Use this project only for systems you own or are explicitly authorized to assess. The current release is offline-only and does not generate network traffic. Do not use it to disrupt services or test third-party systems without written authorization.
