"""Transparent staffing scenarios, not a staffing optimizer or source-system rule."""


def labour_summary(shifts):
    out = shifts.groupby(["store_id", "role"], as_index=False).agg(
        scheduled_hours=("scheduled_hours", "sum"),
        paid_hours=("paid_hours", "sum"),
        wage_cost_gbp=("wage_cost_gbp", "sum"),
        overtime_hours=("overtime_hours", "sum"),
        absent_shifts=("absence_flag", "sum"),
        scheduled_shifts=("shift_id", "size"),
    )
    out["hours_variance"] = out.paid_hours - out.scheduled_hours
    out["absence_shift_pct"] = 100 * out.absent_shifts / out.scheduled_shifts
    return out


def staffing_scenario(forecasts, direct_transactions_per_hour=8.0, manager_hours=10.0):
    if direct_transactions_per_hour <= 0 or manager_hours < 0:
        raise ValueError("Positive productivity and nonnegative manager coverage required")
    f = forecasts[(forecasts.metric == "transactions") & (forecasts.model == "seasonal_naive")]
    keys = ["store_id", "origin_date", "target_date", "horizon_days"]
    out = (
        f.groupby(keys, as_index=False)
        .forecast.sum()
        .rename(columns={"forecast": "forecast_transactions"})
    )
    out["scenario_direct_tph"] = direct_transactions_per_hour
    out["required_direct_hours"] = out.forecast_transactions / direct_transactions_per_hour
    out["manager_cover_hours"] = manager_hours
    out["scenario_total_hours"] = out.required_direct_hours + manager_hours
    return out
