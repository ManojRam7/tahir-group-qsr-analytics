import numpy as np
import pandas as pd
import pytest

from qsr_analytics.did import manual_did
from qsr_analytics.metrics import (
    add_kpis,
    aggregate_kpis,
    parse_duration,
    parse_roster_hours,
    safe_divide,
)


def test_net_sales_already_ex_tax_and_waste_not_double_counted():
    df = pd.DataFrame(
        [
            dict(
                net_sales_gbp=1000.0,
                transactions=100,
                paid_hours=20,
                wage_cost_gbp=200,
                food_cost_gbp=300,
                waste_cost_gbp=20,
                packaging_cost_gbp=15,
                complaints=2,
                forecast_sales_gbp=900,
            )
        ]
    )
    out = add_kpis(df).iloc[0]
    assert out.revenue_ex_vat_gbp == 1000
    assert out.avg_transaction_value_gbp == 10
    assert out.labour_cost_pct == 20
    assert out.contribution_profit_gbp == 485


def test_zero_and_time_formats():
    assert np.isnan(safe_divide(1, 0))
    assert parse_duration("04:28") == 268
    assert parse_roster_hours("123:30") == 123.5
    with pytest.raises(ValueError):
        parse_duration("04:60")


def test_weighted_ratios():
    df = pd.DataFrame(
        dict(
            group=[1, 1],
            net_sales_gbp=[100.0, 900.0],
            transactions=[10, 30],
            paid_hours=[2, 3],
            wage_cost_gbp=[20, 40],
            food_cost_gbp=[30, 100],
            waste_cost_gbp=[1, 2],
            complaints=[0, 1],
            service_total_seconds=[100, 2700],
            service_orders=[1, 9],
        )
    )
    out = aggregate_kpis(df, ["group"]).iloc[0]
    assert out.avg_transaction_value_gbp == 25
    assert out.avg_service_seconds == 280


def test_manual_did():
    df = pd.DataFrame(
        dict(treated_store=[0, 0, 1, 1], post_period=[0, 1, 0, 1], y=[10.0, 11.0, 10.0, 13.0])
    )
    assert manual_did(df, "y")["did_estimate"] == 2
    with pytest.raises(ValueError):
        manual_did(df.iloc[:3], "y")
