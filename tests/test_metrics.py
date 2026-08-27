import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qsr_analytics.metrics import add_kpis
from qsr_analytics.did import manual_did


def test_kpi_math():
    df = pd.DataFrame([
        {
            "net_sales_gbp": 1200.0,
            "transactions": 100,
            "paid_hours": 20,
            "wage_cost_gbp": 200.0,
            "food_cost_gbp": 300.0,
            "waste_cost_gbp": 20.0,
            "complaints": 2,
            "forecast_sales_gbp": 1000.0,
        }
    ])
    out = add_kpis(df).iloc[0]
    assert round(out.revenue_ex_vat_gbp, 2) == 1000.00
    assert round(out.avg_transaction_value_gbp, 2) == 12.00
    assert round(out.transactions_per_paid_hour, 2) == 5.00
    assert round(out.labour_cost_pct, 2) == 20.00
    assert round(out.waste_pct_sales, 2) == 2.00
    assert round(out.complaints_per_1000_orders, 2) == 20.00


def test_manual_did():
    df = pd.DataFrame(
        {
            "treated_store": [0, 0, 1, 1],
            "post_period": [0, 1, 0, 1],
            "y": [10.0, 11.0, 10.0, 13.0],
        }
    )
    result = manual_did(df, "y")
    assert result["treated_change"] == 3.0
    assert result["control_change"] == 1.0
    assert result["did_estimate"] == 2.0
