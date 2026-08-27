from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qsr_analytics.metrics import add_kpis
from qsr_analytics.did import manual_did, fit_twfe_did


def main():
    source = Path("data/generated/store_daily.csv")
    if not source.exists():
        raise FileNotFoundError("Run scripts/generate_synthetic_data.py first")

    df = pd.read_csv(source, parse_dates=["date"])
    df = add_kpis(df)

    required_unique = df.groupby(["store_id", "date"]).size().max()
    if required_unique != 1:
        raise ValueError("store_daily must contain exactly one row per store/date")
    if (df[["transactions", "net_sales_gbp", "paid_hours"]].lt(0)).any().any():
        raise ValueError("Negative operational values detected")

    outcomes = [
        "transactions_per_paid_hour",
        "labour_cost_pct",
        "waste_pct_sales",
        "avg_service_seconds",
        "complaints_per_1000_orders",
        "contribution_profit_gbp",
    ]

    print("\n=== 2x2 Difference-in-Differences ===")
    for outcome in outcomes:
        result = manual_did(df, outcome)
        print(f"{outcome:35s}: {result['did_estimate']:.4f}")

    print("\n=== Two-way fixed-effects DID: productivity ===")
    model = fit_twfe_did(df, "transactions_per_paid_hour")
    beta = model.params["did"]
    se = model.bse["did"]
    p = model.pvalues["did"]
    print(f"effect={beta:.4f}; clustered_SE={se:.4f}; p={p:.6f}")
    print(f"95% CI=({beta - 1.96 * se:.4f}, {beta + 1.96 * se:.4f})")


if __name__ == "__main__":
    main()
