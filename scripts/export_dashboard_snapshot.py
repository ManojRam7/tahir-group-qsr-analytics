"""Reproduce the five reviewed dashboard queries from validated synthetic outputs."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from qsr_analytics.etl import load_tables, validate_tables

ROOT = Path(__file__).resolve().parents[1]


def rows(frame):
    return json.loads(frame.to_json(orient="records", date_format="iso", double_precision=15))


def main():
    tables = load_tables(ROOT / "data/generated")
    validate_tables(tables)
    daily = tables["store_daily"]
    if (daily.store_id.nunique(), daily.date.nunique(), len(daily)) != (12, 112, 1344):
        raise ValueError("This authored dashboard requires the default 12-store, 112-day scenario.")
    if str(daily.date.min())[:10] != "2026-01-05" or str(daily.date.max())[:10] != "2026-04-26":
        raise ValueError("Update dashboard captions explicitly for a different date window.")
    snapshot = json.loads((ROOT / "dashboard/snapshot_template.json").read_text())
    analysis = json.loads((ROOT / "reports/generated/analysis.json").read_text())
    data = {
        "daily": rows(daily),
        "channels": rows(
            tables["sales"]
            .groupby(["store_id", "channel", "daypart"], as_index=False)[
                ["transactions", "net_sales_gbp"]
            ]
            .sum()
        ),
        "forecasts": rows(pd.read_csv(ROOT / "reports/generated/forecast_scores.csv")),
        "events": rows(pd.read_csv(ROOT / "reports/generated/event_study.csv")),
        "did": [
            {
                **analysis["manual"],
                **analysis["twfe"],
                "placebo": analysis["pre_period_placebo"]["did_estimate"],
            }
        ],
    }
    for key, value in data.items():
        snapshot["queries"][key]["rows"] = value
    snapshot["generatedAt"] = datetime.now(timezone.utc).isoformat()
    snapshot["buildStatus"] = "complete"
    target = ROOT / "reports/generated/dashboard_snapshot.json"
    target.write_text(json.dumps(snapshot, allow_nan=False) + "\n")
    print(
        "Dashboard snapshot exported from validated synthetic data:",
        {key: len(value) for key, value in data.items()},
    )


if __name__ == "__main__":
    main()
