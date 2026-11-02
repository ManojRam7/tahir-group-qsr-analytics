"""Synthetic staging contracts, reconciliation, and one-to-one operational mart."""

import numpy as np
import pandas as pd

KEY = ["store_id", "date"]
GRAINS = {
    "stores": ["store_id"],
    "items": ["item_id"],
    "sales": KEY + ["channel", "daypart"],
    "employee_shifts": ["shift_id"],
    "service": KEY + ["daypart"],
    "delivery": KEY + ["platform"],
    "availability": KEY + ["daypart", "item_id"],
    "upgrades": KEY + ["daypart"],
    "purchase_orders": ["order_id", "line_id"],
    "receipts": ["receipt_id"],
    "stock": KEY + ["item_id"],
    "transfers": ["transfer_id"],
    "waste": ["waste_id"],
    "stock_counts": KEY + ["item_id"],
    "forecasts": [
        "store_id",
        "channel",
        "origin_date",
        "target_date",
        "horizon_days",
        "model",
        "metric",
    ],
    "store_daily": KEY,
}


def assert_grain(df, key, name):
    if df.empty or df[key].isna().any().any() or df.duplicated(key).any():
        raise ValueError(f"{name}: empty, null key or duplicate grain {key}")


def stock_usage(stock):
    out = stock.copy()
    out["actual_usage_units"] = (
        out.opening_units
        + out.received_units
        + out.transfer_in_units
        - out.transfer_out_units
        - out.closing_units
    )
    out["unexplained_units"] = (
        out.actual_usage_units - out.theoretical_usage_units - out.waste_units
    )
    out["usage_cost_gbp"] = out.actual_usage_units * out.unit_cost_gbp
    out["waste_cost_gbp"] = out.waste_units * out.unit_cost_gbp
    return out


def _aggregate(df, columns):
    return df.groupby(KEY, as_index=False)[columns].sum(min_count=1)


def build_mart(t):
    sales = t["sales"]
    out = _aggregate(sales, ["transactions", "net_sales_gbp", "tax_gbp", "gross_sales_gbp"])
    shifts = t["employee_shifts"].copy()
    shifts["direct_hours"] = shifts.paid_hours.where(shifts.role == "team", 0)
    shifts["manager_hours"] = shifts.paid_hours.where(shifts.role == "manager", 0)
    shifts["team_wage_cost_gbp"] = shifts.wage_cost_gbp.where(shifts.role == "team", 0)
    shift_daily = _aggregate(
        shifts,
        [
            "paid_hours",
            "scheduled_hours",
            "wage_cost_gbp",
            "direct_hours",
            "manager_hours",
            "team_wage_cost_gbp",
            "overtime_hours",
            "absence_flag",
        ],
    )
    inventory = stock_usage(t["stock"])
    # Total inventory usage includes packaging; food KPI excludes packaging explicitly.
    inventory = inventory.merge(
        t["items"][["item_id", "category"]], on="item_id", validate="many_to_one"
    )
    inventory["food_cost_gbp"] = inventory.usage_cost_gbp.where(inventory.category == "food", 0)
    inventory["packaging_cost_gbp"] = inventory.usage_cost_gbp.where(
        inventory.category == "packaging", 0
    )
    inventory["waste_cost_gbp"] = inventory.waste_cost_gbp.where(inventory.category == "food", 0)
    parts = [
        shift_daily,
        _aggregate(inventory, ["food_cost_gbp", "packaging_cost_gbp", "waste_cost_gbp"]),
        _aggregate(t["service"], ["service_orders", "service_total_seconds", "complaints"]),
        _aggregate(
            t["delivery"],
            [
                "accepted_orders",
                "offered_orders",
                "rejected_orders",
                "handoff_orders",
                "handoff_total_seconds",
                "delivery_accuracy_eligible_orders",
                "delivery_issue_orders",
                "offline_minutes",
                "scheduled_minutes",
            ],
        ),
        _aggregate(
            t["availability"],
            ["eligible_minutes", "available_minutes", "gold_checks", "gold_passes"],
        ),
        _aggregate(
            t["upgrades"],
            [
                "upgrade_eligible_transactions",
                "upgraded_transactions",
                "incremental_upgrade_sales_gbp",
            ],
        ),
        _aggregate(sales[sales.channel == "delivery"], ["net_sales_gbp"]).rename(
            columns={"net_sales_gbp": "delivery_net_sales_gbp"}
        ),
    ]
    for part in parts:
        out = out.merge(part, on=KEY, how="left", validate="one_to_one")
    out = out.merge(t["stores"], on="store_id", validate="many_to_one")
    out["post_period"] = (pd.to_datetime(out.date) >= pd.Timestamp("2026-03-02")).astype(int)
    # Partial warm-up coverage stays null; no zero-fill of unissued forecasts.
    f = t["forecasts"]
    f = f[(f.model == "seasonal_naive") & (f.metric == "net_sales_gbp")].copy()
    f["date"] = pd.to_datetime(f.target_date).dt.strftime("%Y-%m-%d")
    f = _aggregate(f, ["forecast"]).rename(columns={"forecast": "forecast_sales_gbp"})
    return out.merge(f, on=KEY, how="left", validate="one_to_one")


def _equal(a, b, label, atol=1e-6):
    if not np.allclose(a, b, rtol=0, atol=atol, equal_nan=False):
        raise ValueError(f"Reconciliation failed: {label}")


def validate_tables(t):
    for name, key in GRAINS.items():
        assert_grain(t[name], key, name)
        df = t[name]
        required_values = df.drop(columns=["forecast_sales_gbp"], errors="ignore")
        if required_values.isna().any().any():
            raise ValueError(f"{name}: missing data")
        numeric = df.select_dtypes(include="number")
        numeric = numeric.drop(columns=["forecast_sales_gbp"], errors="ignore")
        if not np.isfinite(numeric).all().all() or numeric.lt(0).any().any():
            raise ValueError(f"{name}: negative or nonfinite value")
        if "store_id" in df and not df.store_id.isin(t["stores"].store_id).all():
            raise ValueError(f"{name}: orphan store")
        if "item_id" in df and not df.item_id.isin(t["items"].item_id).all():
            raise ValueError(f"{name}: orphan item")
    sales_keys = set(map(tuple, t["sales"][KEY].drop_duplicates().to_numpy()))
    for name in [
        "employee_shifts",
        "service",
        "delivery",
        "upgrades",
        "availability",
        "stock",
        "waste",
        "stock_counts",
    ]:
        keys = set(map(tuple, t[name][KEY].drop_duplicates().to_numpy()))
        if keys != sales_keys:
            raise ValueError(f"{name}: missing or extraneous store-day coverage")
    s = t["sales"]
    _equal(s.gross_sales_gbp, s.net_sales_gbp + s.tax_gbp, "gross=net+tax", 0.011)
    hours = t["employee_shifts"]
    if ((hours.absence_flag == 1) & (hours.paid_hours != 0)).any():
        raise ValueError("Absent shifts cannot carry paid hours in this scenario")
    if not hours.role.isin(["team", "manager"]).all() or (hours.paid_hours > 12).any():
        raise ValueError("Invalid synthetic role or shift length")
    _equal(
        hours.wage_cost_gbp,
        (hours.paid_hours * hours.hourly_rate_gbp).round(2),
        "shift wages",
        0.011,
    )
    ledger = stock_usage(t["stock"]).sort_values(["store_id", "item_id", "date"])
    previous = ledger.groupby(["store_id", "item_id"]).closing_units.shift()
    mask = previous.notna()
    _equal(ledger.loc[mask, "opening_units"], previous[mask], "stock continuity", 0.0002)
    if (ledger.actual_usage_units < 0).any() or (ledger.unexplained_units < -0.0002).any():
        raise ValueError("Invalid stock balance")
    r = t["receipts"].merge(
        t["purchase_orders"],
        on=["order_id", "line_id"],
        validate="many_to_one",
        suffixes=("", "_po"),
        indicator=True,
    )
    if not (r._merge == "both").all() or (r.receipt_date < r.order_date).any():
        raise ValueError("Receipt without valid earlier purchase order")
    for col in ["store_id", "item_id"]:
        if not (r[col] == r[col + "_po"]).all():
            raise ValueError("Receipt/PO identity mismatch")
    _equal(r.received_units, r.received_cases * r.units_per_case, "receipt case conversion")
    _equal(r.receipt_value_gbp, r.received_cases * r.case_price_gbp, "receipt value", 0.011)
    receipt_qty = t["receipts"].groupby(["order_id", "line_id"]).received_cases.sum()
    ordered = t["purchase_orders"].set_index(["order_id", "line_id"]).ordered_cases
    if (receipt_qty > ordered.reindex(receipt_qty.index)).any():
        raise ValueError("Over-receipt requires explicit exception")
    received = t["receipts"].rename(columns={"receipt_date": "date"})
    check = t["stock"].merge(
        received.groupby(KEY + ["item_id"], as_index=False).received_units.sum(),
        on=KEY + ["item_id"],
        how="left",
        suffixes=("", "_receipt"),
        validate="one_to_one",
    )
    _equal(check.received_units, check.received_units_receipt.fillna(0), "receipts to ledger")
    for name, numerator, denominator in [
        ("availability", "available_minutes", "eligible_minutes"),
        ("availability", "gold_passes", "gold_checks"),
        ("delivery", "delivery_issue_orders", "delivery_accuracy_eligible_orders"),
        ("delivery", "offline_minutes", "scheduled_minutes"),
        ("upgrades", "upgraded_transactions", "upgrade_eligible_transactions"),
    ]:
        if (t[name][numerator] > t[name][denominator]).any():
            raise ValueError(f"{name}: numerator exceeds eligible population")
    for name, value, ledger_value in [
        ("waste", "waste_units", "waste_units"),
        ("stock_counts", "closing_units", "closing_units"),
    ]:
        v = t[name].groupby(KEY + ["item_id"])[value].sum().sort_index()
        expected = t["stock"].set_index(KEY + ["item_id"])[ledger_value].sort_index()
        _equal(v.reindex(expected.index), expected, f"{name} to ledger")
    for direction, col in [
        ("from_store_id", "transfer_out_units"),
        ("to_store_id", "transfer_in_units"),
    ]:
        tr = t["transfers"].rename(columns={direction: "store_id"})
        if not tr.store_id.isin(t["stores"].store_id).all():
            raise ValueError("Orphan transfer endpoint")
        v = tr.groupby(KEY + ["item_id"]).units.sum()
        expected = t["stock"].set_index(KEY + ["item_id"])[col]
        _equal(v.reindex(expected.index).fillna(0), expected, "transfer conservation")
    d = t["delivery"]
    _equal(d.offered_orders, d.accepted_orders + d.rejected_orders, "delivery orders")
    # Cross-fact populations: timing/upgrade counters and channel orders must agree.
    totals = _aggregate(t["sales"], ["transactions"]).set_index(KEY).sort_index()
    for name, col in [("service", "service_orders"), ("upgrades", "upgrade_eligible_transactions")]:
        counter = _aggregate(t[name], [col]).set_index(KEY).sort_index()
        _equal(counter[col].reindex(totals.index), totals.transactions, f"{name} order coverage")
    delivery_sales = _aggregate(t["sales"][t["sales"].channel == "delivery"], ["transactions"])
    accepted = _aggregate(t["delivery"], ["accepted_orders"])
    _equal(
        accepted.set_index(KEY).accepted_orders.sort_index(),
        delivery_sales.set_index(KEY).transactions.sort_index(),
        "delivery channel population",
    )
    f = t["forecasts"]
    actuals = (
        t["sales"]
        .groupby(KEY + ["channel"], as_index=False)[["net_sales_gbp", "transactions"]]
        .sum()
    )
    actuals = actuals.melt(id_vars=KEY + ["channel"], var_name="metric", value_name="source_actual")
    actuals = actuals.rename(columns={"date": "target_date"})
    actuals["target_date"] = pd.to_datetime(actuals.target_date)
    joined = f.assign(target_date=pd.to_datetime(f.target_date)).merge(
        actuals,
        on=["store_id", "target_date", "channel", "metric"],
        how="left",
        validate="many_to_one",
    )
    _equal(joined.actual, joined.source_actual, "forecast actual alignment")
    delta = pd.to_datetime(f.target_date) - pd.to_datetime(f.origin_date)
    if not (delta.dt.days == f.horizon_days).all() or (f.horizon_days < 1).any():
        raise ValueError("Forecast horizon/origin violation")
    # Rebuild checks source-to-mart joins and every additive output, not just row count.
    rebuilt = build_mart(t).sort_values(KEY).reset_index(drop=True)
    actual = t["store_daily"].sort_values(KEY).reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, rebuilt, check_dtype=False)
    return {name: len(df) for name, df in t.items()}


def load_tables(directory):
    from pathlib import Path

    return {name: pd.read_csv(Path(directory) / f"{name}.csv") for name in GRAINS}
