from copy import deepcopy
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pytest

from qsr_analytics.did import fit_twfe_did, validate_panel
from qsr_analytics.etl import stock_usage, validate_tables
from qsr_analytics.forecasting import forecast_scores, rolling_forecasts
from qsr_analytics.metrics import aggregate_kpis
from scripts.generate_synthetic_data import generate_tables


@pytest.fixture(scope="module")
def tables():
    return generate_tables(n_stores=4, days=70)


def test_pipeline_and_reproducibility(tables):
    assert validate_tables(tables)["store_daily"] == 280
    again = generate_tables(n_stores=4, days=70)
    for name in tables:
        pd.testing.assert_frame_equal(tables[name], again[name])
    usage = stock_usage(tables["stock"])
    assert usage.unexplained_units.min() >= -0.0002
    assert (tables["stock"].closing_units >= 0).all()


@pytest.mark.parametrize(
    "table,column",
    [
        ("sales", "net_sales_gbp"),
        ("receipts", "received_units"),
        ("employee_shifts", "wage_cost_gbp"),
        ("stock", "opening_units"),
        ("waste", "waste_units"),
        ("transfers", "units"),
        ("stock_counts", "closing_units"),
    ],
)
def test_reject_corruption(tables, table, column):
    bad = deepcopy(tables)
    bad[table].loc[1, column] += 3
    with pytest.raises((ValueError, AssertionError)):
        validate_tables(bad)


def test_duplicate_and_orphan(tables):
    bad = deepcopy(tables)
    bad["sales"] = pd.concat([bad["sales"], bad["sales"].iloc[:1]])
    with pytest.raises(ValueError):
        validate_tables(bad)
    bad = deepcopy(tables)
    bad["receipts"].loc[0, "item_id"] = "UNKNOWN"
    with pytest.raises(ValueError):
        validate_tables(bad)


def test_forecast_has_no_lookahead(tables):
    original = rolling_forecasts(tables["sales"])
    changed = tables["sales"].copy()
    cutoff = "2026-02-10"
    changed.loc[changed.date >= cutoff, "net_sales_gbp"] *= 20
    new = rolling_forecasts(changed)
    mask = original.origin_date < pd.Timestamp(cutoff)
    pd.testing.assert_series_equal(original.loc[mask, "forecast"], new.loc[mask, "forecast"])
    assert (original.origin_date < original.target_date).all()
    missing = tables["sales"][tables["sales"].date != cutoff]
    with pytest.raises(ValueError):
        rolling_forecasts(missing)


def test_wape_does_not_cancel():
    df = pd.DataFrame(
        dict(
            model=["a", "a"],
            metric=["sales", "sales"],
            horizon_days=[7, 7],
            actual=[100.0, 100.0],
            forecast=[80.0, 120.0],
        )
    )
    score = forecast_scores(df).iloc[0]
    assert score.wape_pct == 20
    assert score.bias_pct == 0


def test_sql_python_parity(tables):
    con = duckdb.connect()
    for name in ["store_daily", "stock", "forecasts"]:
        con.register(name, tables[name])
    sql = con.execute(Path("sql/operational_kpis.sql").read_text()).df().sort_values("store_id")
    py = aggregate_kpis(tables["store_daily"], ["store_id"]).sort_values("store_id")
    for name in sql.select_dtypes("number"):
        np.testing.assert_allclose(sql[name], py[name], rtol=1e-10)
    queries = Path("sql/inventory_and_forecasts.sql").read_text().split(";")
    inv = con.execute(queries[0]).df()
    np.testing.assert_allclose(
        inv.actual_usage_units, stock_usage(tables["stock"]).actual_usage_units
    )
    scores = con.execute(queries[1]).df().sort_values(["model", "metric"])
    py_scores = forecast_scores(tables["forecasts"]).sort_values(["model", "metric"])
    np.testing.assert_allclose(scores.wape_pct, py_scores.wape_pct)


def test_did_panel_and_injected_effect():
    dates = pd.date_range("2026-01-01", periods=28)
    rows = [
        dict(
            store_id=f"S{s}",
            date=str(d.date()),
            treated_store=s % 2,
            post_period=int(i >= 14),
            y=10 + s + i * 0.1 + 2 * (s % 2) * int(i >= 14),
        )
        for s in range(6)
        for i, d in enumerate(dates)
    ]
    df = pd.DataFrame(rows)
    with pytest.warns(UserWarning, match="clusters"):
        fit = fit_twfe_did(df, "y")
    assert fit.params["did"] == pytest.approx(2, abs=1e-9)
    assert fit.use_t
    assert fit.nobs == len(df)
    for bad in [df.iloc[:-1], pd.concat([df, df.iloc[:1]])]:
        with pytest.raises(ValueError):
            validate_panel(bad, "y")
    df.loc[0, "y"] = np.nan
    with pytest.raises(ValueError):
        fit_twfe_did(df, "y")


def test_labour_scenario_uses_forecast_only(tables):
    from qsr_analytics.labour import labour_summary, staffing_scenario

    original = staffing_scenario(tables["forecasts"])
    changed = tables["forecasts"].copy()
    changed["actual"] = 999999
    pd.testing.assert_frame_equal(original, staffing_scenario(changed))
    assert np.allclose(original.required_direct_hours, original.forecast_transactions / 8)
    summary = labour_summary(tables["employee_shifts"])
    assert np.isclose(summary.wage_cost_gbp.sum(), tables["employee_shifts"].wage_cost_gbp.sum())
    with pytest.raises(ValueError):
        staffing_scenario(changed, direct_transactions_per_hour=0)


@pytest.mark.parametrize(
    "table,column",
    [("service", "service_orders"), ("forecasts", "actual"), ("delivery", "accepted_orders")],
)
def test_cross_fact_populations(tables, table, column):
    bad = deepcopy(tables)
    bad[table].loc[0, column] += 1
    with pytest.raises(ValueError):
        validate_tables(bad)


def test_unmatched_fact_coverage(tables):
    bad = deepcopy(tables)
    extra = bad["employee_shifts"].iloc[:1].copy()
    extra["date"] = "2025-12-31"
    extra["shift_id"] = "EXTRA"
    bad["employee_shifts"] = pd.concat([bad["employee_shifts"], extra])
    with pytest.raises(ValueError, match="coverage"):
        validate_tables(bad)


def test_publication_guard():
    from scripts.check_publication import problems

    assert problems(Path("attachment.pdf"), "")
    assert problems(Path("contact.txt"), "someone" + "@" + "example.org")
    assert not problems(Path("docs/note.md"), "Fictional Restaurant 1")
