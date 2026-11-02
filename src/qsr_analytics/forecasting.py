"""Calendar-aware rolling-origin baselines. No future actual enters a prediction."""

import numpy as np
import pandas as pd

from .metrics import safe_divide


def rolling_forecasts(sales, horizon=7, min_history=28):
    if horizon < 1 or min_history < 7:
        raise ValueError("horizon >= 1 and min_history >= 7 required")
    daily = sales.groupby(["store_id", "channel", "date"], as_index=False)[
        ["net_sales_gbp", "transactions"]
    ].sum()
    daily["date"] = pd.to_datetime(daily.date)
    rows = []
    for (store, channel), group in daily.groupby(["store_id", "channel"]):
        group = group.sort_values("date").set_index("date")
        if len(group) != len(pd.date_range(group.index.min(), group.index.max())):
            raise ValueError("Missing calendar dates; never shift across gaps")
        for target in group.index[min_history + horizon - 1 :]:
            origin = target - pd.Timedelta(days=horizon)
            history = group.loc[:origin]
            same_weekday = history[history.index.dayofweek == target.dayofweek].tail(4)
            for model in ["seasonal_naive", "weekday_mean_4"]:
                prediction = (
                    same_weekday.iloc[-1]
                    if model == "seasonal_naive"
                    else same_weekday.mean(numeric_only=True)
                )
                for metric in ["net_sales_gbp", "transactions"]:
                    rows.append(
                        dict(
                            store_id=store,
                            channel=channel,
                            target_date=target,
                            origin_date=origin,
                            horizon_days=horizon,
                            model=model,
                            metric=metric,
                            forecast=float(prediction[metric]),
                            actual=float(group.loc[target, metric]),
                        )
                    )
    return pd.DataFrame(rows)


def forecast_scores(forecasts):
    rows = []
    for keys, g in forecasts.groupby(["model", "metric", "horizon_days"]):
        if g[["forecast", "actual"]].isna().any().any() or (g.actual < 0).any():
            raise ValueError("Scores require complete nonnegative actuals")
        error = g.forecast - g.actual
        rows.append(
            dict(
                zip(["model", "metric", "horizon_days"], keys),
                n=len(g),
                mae=float(error.abs().mean()),
                rmse=float(np.sqrt((error**2).mean())),
                wape_pct=float(100 * safe_divide(error.abs().sum(), g.actual.sum())),
                bias_pct=float(100 * safe_divide(error.sum(), g.actual.sum())),
            )
        )
    return pd.DataFrame(rows)
