"""Portfolio definitions, not certified source-system formulas. Percent outputs use 0..100."""

from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(numerator, denominator):
    n, d = np.broadcast_arrays(np.asarray(numerator, float), np.asarray(denominator, float))
    return np.divide(n, d, out=np.full(n.shape, np.nan), where=np.isfinite(d) & (d != 0))


def parse_duration(value: str) -> int:
    """Parse elapsed mm:ss (minutes may exceed 59), never decimal minutes."""
    minutes, seconds = value.split(":")
    if not minutes.isdigit() or not seconds.isdigit() or not 0 <= int(seconds) < 60:
        raise ValueError("Expected nonnegative mm:ss")
    return 60 * int(minutes) + int(seconds)


def parse_roster_hours(value: str) -> float:
    """Roster HHH:MM is hours/minutes, unlike service mm:ss."""
    hours, minutes = value.split(":")
    if not hours.isdigit() or not minutes.isdigit() or not 0 <= int(minutes) < 60:
        raise ValueError("Expected nonnegative hours:minutes")
    return int(hours) + int(minutes) / 60


def add_kpis(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # Breaking correction: net is already ex-tax. No hard-coded VAT conversion.
    out["revenue_ex_vat_gbp"] = out["net_sales_gbp"]
    ratios = {
        "avg_transaction_value_gbp": ("net_sales_gbp", "transactions", 1),
        "transactions_per_paid_hour": ("transactions", "paid_hours", 1),
        "sales_per_paid_hour_gbp": ("net_sales_gbp", "paid_hours", 1),
        "labour_cost_pct": ("wage_cost_gbp", "net_sales_gbp", 100),
        "food_cost_pct": ("food_cost_gbp", "net_sales_gbp", 100),
        "waste_pct_sales": ("waste_cost_gbp", "net_sales_gbp", 100),
        "complaints_per_1000_orders": ("complaints", "transactions", 1000),
        "direct_transactions_per_hour": ("transactions", "direct_hours", 1),
        "team_labour_cost_pct": ("team_wage_cost_gbp", "net_sales_gbp", 100),
        "delivery_sales_mix_pct": ("delivery_net_sales_gbp", "net_sales_gbp", 100),
        "upgrade_rate_pct": ("upgraded_transactions", "upgrade_eligible_transactions", 100),
        "availability_pct": ("available_minutes", "eligible_minutes", 100),
        "delivery_issue_pct": ("delivery_issue_orders", "delivery_accuracy_eligible_orders", 100),
        "driver_handoff_seconds": ("handoff_total_seconds", "handoff_orders", 1),
        "avg_service_seconds": ("service_total_seconds", "service_orders", 1),
        "rejection_pct": ("rejected_orders", "offered_orders", 100),
        "offline_pct": ("offline_minutes", "scheduled_minutes", 100),
    }
    for name, (n, d, scale) in ratios.items():
        if n in out and d in out:
            out[name] = scale * safe_divide(out[n], out[d])
    if "forecast_sales_gbp" in out:
        out["forecast_error_gbp"] = out.net_sales_gbp - out.forecast_sales_gbp
        out["absolute_percentage_error_pct"] = 100 * np.abs(
            safe_divide(out.forecast_error_gbp, out.net_sales_gbp)
        )
    out["gross_profit_gbp"] = out.net_sales_gbp - out.food_cost_gbp
    # food_cost is total actual usage INCLUDING recorded waste.
    out["contribution_profit_gbp"] = (
        out.gross_profit_gbp - out.wage_cost_gbp - out.get("packaging_cost_gbp", 0)
    )
    return out


def aggregate_kpis(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Ratio-of-sums. Only additive primitives enter this function."""
    primitives = [
        c
        for c in df
        if c.endswith("_gbp")
        and c
        in {
            "gross_sales_gbp",
            "net_sales_gbp",
            "tax_gbp",
            "wage_cost_gbp",
            "food_cost_gbp",
            "waste_cost_gbp",
            "packaging_cost_gbp",
            "team_wage_cost_gbp",
            "delivery_net_sales_gbp",
        }
    ]
    primitives += [
        c
        for c in [
            "transactions",
            "paid_hours",
            "direct_hours",
            "complaints",
            "service_total_seconds",
            "service_orders",
            "handoff_total_seconds",
            "handoff_orders",
            "available_minutes",
            "eligible_minutes",
            "upgraded_transactions",
            "upgrade_eligible_transactions",
            "delivery_issue_orders",
            "delivery_accuracy_eligible_orders",
            "rejected_orders",
            "offered_orders",
            "offline_minutes",
            "scheduled_minutes",
        ]
        if c in df
    ]
    return add_kpis(df.groupby(by, as_index=False)[primitives].sum(min_count=1))
