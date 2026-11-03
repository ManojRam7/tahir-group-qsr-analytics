"""Validate detail -> operational mart -> forecasts and educational causal diagnostics."""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from qsr_analytics.did import event_study, fit_twfe_did, manual_did, pretrend_diagnostics
from qsr_analytics.etl import load_tables, validate_tables
from qsr_analytics.forecasting import forecast_scores
from qsr_analytics.labour import labour_summary, staffing_scenario
from qsr_analytics.metrics import add_kpis, aggregate_kpis


def main():
    t = load_tables("data/generated")
    counts = validate_tables(t)
    df = add_kpis(t["store_daily"])
    output = Path("reports/generated")
    output.mkdir(parents=True, exist_ok=True)
    forecast_scores(t["forecasts"]).to_csv(output / "forecast_scores.csv", index=False)
    aggregate_kpis(t["store_daily"], ["treated_store", "post_period"]).to_csv(
        output / "group_period_kpis.csv", index=False
    )
    labour_summary(t["employee_shifts"]).to_csv(output / "labour_summary.csv", index=False)
    staffing_scenario(t["forecasts"]).to_csv(output / "staffing_scenarios.csv", index=False)
    df.to_csv(output / "daily_kpis.csv", index=False)
    outcome = "transactions_per_paid_hour"
    model = fit_twfe_did(df, outcome)
    trend, placebo = pretrend_diagnostics(df, outcome)
    trend.to_csv(output / "pretrends.csv")
    event_study(df, outcome).to_csv(output / "event_study.csv", index=False)
    ci = model.conf_int().loc["did"].tolist()
    result = dict(
        synthetic_only=True,
        validated_rows=counts,
        manual=manual_did(df, outcome),
        twfe=dict(
            estimate=model.params["did"],
            se=model.bse["did"],
            p=model.pvalues["did"],
            ci_95=ci,
            clusters=int(df.store_id.nunique()),
        ),
        pre_period_placebo=placebo,
        caveat="Few clusters; injected scenario effects, no real business causal claims.",
    )
    (output / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    pd.DataFrame(
        [
            {
                "synthetic_only": True,
                "outcome": outcome,
                "intervention_date": "2026-03-02",
                "treated_stores": int(df.loc[df.treated_store == 1, "store_id"].nunique()),
                "comparison_stores": int(df.loc[df.treated_store == 0, "store_id"].nunique()),
                **result["manual"],
                "ci_low": ci[0],
                "ci_high": ci[1],
                "placebo": placebo["did_estimate"],
            }
        ]
    ).to_csv(output / "did_results.csv", index=False)
    print(json.dumps(result, indent=2))
    print(pd.read_csv(output / "forecast_scores.csv").to_string(index=False))


if __name__ == "__main__":
    main()
