from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(numerator, denominator):
    """Vectorised division returning NaN where denominator is zero."""
    denominator = np.asarray(denominator, dtype=float)
    numerator = np.asarray(numerator, dtype=float)
    return np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, np.nan, dtype=float),
        where=denominator != 0,
    )


def add_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Create the operational KPIs used throughout the project.

    Expected grain: one row per store per trading day.
    """
    out = df.copy()
    out["revenue_ex_vat_gbp"] = out["net_sales_gbp"] / 1.20
    out["avg_transaction_value_gbp"] = safe_divide(out["net_sales_gbp"], out["transactions"])
    out["transactions_per_paid_hour"] = safe_divide(out["transactions"], out["paid_hours"])
    out["sales_per_paid_hour_gbp"] = safe_divide(out["net_sales_gbp"], out["paid_hours"])
    out["labour_cost_pct"] = 100 * safe_divide(out["wage_cost_gbp"], out["revenue_ex_vat_gbp"])
    out["food_cost_pct"] = 100 * safe_divide(out["food_cost_gbp"], out["revenue_ex_vat_gbp"])
    out["waste_pct_sales"] = 100 * safe_divide(out["waste_cost_gbp"], out["revenue_ex_vat_gbp"])
    out["complaints_per_1000_orders"] = 1000 * safe_divide(out["complaints"], out["transactions"])
    out["forecast_error_gbp"] = out["net_sales_gbp"] - out["forecast_sales_gbp"]
    out["absolute_percentage_error_pct"] = 100 * np.abs(
        safe_divide(out["forecast_error_gbp"], out["net_sales_gbp"])
    )
    out["gross_profit_gbp"] = out["revenue_ex_vat_gbp"] - out["food_cost_gbp"]
    out["contribution_profit_gbp"] = (
        out["revenue_ex_vat_gbp"]
        - out["food_cost_gbp"]
        - out["wage_cost_gbp"]
        - out["waste_cost_gbp"]
    )
    return out
