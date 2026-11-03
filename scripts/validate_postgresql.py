"""Read-only PostgreSQL parity checks; connection uses standard PG* environment variables.

Run after loading a fresh exercise database. PSQL_BIN can select a local psql executable.
No credentials are written to files or printed.
"""

import io
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from qsr_analytics.etl import stock_usage
from qsr_analytics.forecasting import forecast_scores
from qsr_analytics.metrics import add_kpis

ROOT = Path(__file__).resolve().parents[1]


def query(sql):
    result = subprocess.run(
        [os.environ.get("PSQL_BIN", "psql"), "-X", "--csv", "-v", "ON_ERROR_STOP=1", "-c", sql],
        capture_output=True,
        text=True,
        check=True,
    )
    return pd.read_csv(io.StringIO(result.stdout))


def main():
    manifest = pd.read_csv(ROOT / "sql/postgresql/import_manifest.csv")
    for row in manifest.itertuples():
        expected = pd.read_csv(ROOT / "data/generated" / f"{row.table}.csv")
        assert query(f"SELECT COUNT(*) AS n FROM qsr.{row.table}").n.iloc[0] == len(expected)
    daily = pd.read_csv(ROOT / "data/generated/store_daily.csv")
    actual = query("SELECT * FROM qsr.v_daily_kpis ORDER BY store_id,date")
    expected = (
        add_kpis(daily)
        .sort_values(["store_id", "date"])
        .rename(columns={"sales_per_paid_hour_gbp": "sales_per_paid_hour"})
    )
    fields = [
        "transactions_per_paid_hour",
        "sales_per_paid_hour",
        "labour_cost_pct",
        "team_labour_cost_pct",
    ]
    for field in fields:
        np.testing.assert_allclose(actual[field], expected[field], rtol=1e-10)
    actual_stock = query("SELECT * FROM qsr.v_inventory_balance ORDER BY store_id,date,item_id")
    expected_stock = stock_usage(pd.read_csv(ROOT / "data/generated/stock.csv")).sort_values(
        ["store_id", "date", "item_id"]
    )
    np.testing.assert_allclose(actual_stock.unexplained_units, expected_stock.unexplained_units)
    actual_scores = query("SELECT * FROM qsr.v_forecast_scores ORDER BY model,metric,horizon_days")
    expected_scores = forecast_scores(
        pd.read_csv(ROOT / "data/generated/forecasts.csv")
    ).sort_values(["model", "metric", "horizon_days"])
    for field in ["mae", "rmse", "wape_pct", "bias_pct"]:
        np.testing.assert_allclose(actual_scores[field], expected_scores[field], rtol=1e-10)
    analysis = json.loads((ROOT / "reports/generated/analysis.json").read_text())
    means = query("""
        WITH m AS (SELECT treated_store,post_period,AVG(transactions_per_paid_hour) AS y
        FROM qsr.v_daily_kpis GROUP BY treated_store,post_period)
        SELECT SUM(CASE WHEN treated_store=post_period THEN y ELSE -y END) AS did FROM m
    """)
    np.testing.assert_allclose(means.did.iloc[0], analysis["manual"]["did_estimate"], rtol=1e-10)
    print(
        "PostgreSQL: all 16 row counts, daily ratios, stock, forecast scores and DID match Python."
    )


if __name__ == "__main__":
    main()
