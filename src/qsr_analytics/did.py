"""Common-date, balanced-panel educational DID; staggered adoption is rejected."""

import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def _cells(df, outcome):
    cols = ["treated_store", "post_period", outcome]
    if df[cols].isna().any().any() or not np.isfinite(df[outcome]).all():
        raise ValueError("DID cannot silently drop missing/nonfinite outcomes")
    for col in cols[:2]:
        if not df[col].isin([0, 1]).all():
            raise ValueError("DID flags must be binary")
    means = df.groupby(cols[:2])[outcome].mean()
    if set(means.index) != {(0, 0), (0, 1), (1, 0), (1, 1)}:
        raise ValueError("All four treatment/period cells required")
    return means


def validate_panel(df, outcome):
    _cells(df, outcome)
    if not outcome.isidentifier() or outcome not in df:
        raise ValueError("Outcome must be a column identifier")
    if df[["store_id", "date"]].isna().any().any():
        raise ValueError("Null panel key")
    if df.duplicated(["store_id", "date"]).any():
        raise ValueError("Duplicate store/date")
    if df.groupby("store_id").treated_store.nunique().max() != 1:
        raise ValueError("Treatment membership must be stable")
    if df.groupby("date").post_period.nunique().max() != 1:
        raise ValueError("Only common-date adoption is supported")
    if not df.groupby("date").post_period.first().sort_index().is_monotonic_increasing:
        raise ValueError("Post flag must follow a single cutoff")
    expected = df.store_id.nunique() * df.date.nunique()
    if len(df) != expected:
        raise ValueError("Balanced panel required; inspect missing store/dates")
    if df.store_id.nunique() < 4 or df.groupby("treated_store").store_id.nunique().min() < 2:
        raise ValueError("At least two stores per group required for clustered inference")
    return df.copy()


def manual_did(df, outcome):
    """Equal store-day mean outcome; not ratio-of-sums portfolio productivity."""
    means = _cells(df, outcome)
    a, b, c, d = (float(means.loc[k]) for k in [(0, 0), (0, 1), (1, 0), (1, 1)])
    return dict(
        control_pre=a,
        control_post=b,
        treated_pre=c,
        treated_post=d,
        treated_change=d - c,
        control_change=b - a,
        did_estimate=(d - c) - (b - a),
    )


def fit_twfe_did(df, outcome):
    data = validate_panel(df, outcome)
    clusters = data.store_id.nunique()
    if clusters < 30:
        warnings.warn(
            f"Only {clusters} store clusters; inference is illustrative, not robust evidence.",
            UserWarning,
            stacklevel=2,
        )
    data["did"] = data.treated_store * data.post_period
    return smf.ols(f"{outcome} ~ did + C(store_id) + C(date)", data=data).fit(
        cov_type="cluster",
        use_t=True,
        cov_kwds={"groups": data.store_id, "use_correction": True, "df_correction": True},
    )


def pretrend_diagnostics(df, outcome):
    """Weekly group gaps and a fake mid-pre launch. Neither proves parallel trends."""
    data = validate_panel(df, outcome)
    pre = data[data.post_period == 0].copy()
    pre["week"] = pd.to_datetime(pre.date).dt.to_period("W-SUN").astype(str)
    trend = pre.groupby(["week", "treated_store"])[outcome].mean().unstack()
    trend["treated_minus_control"] = trend[1] - trend[0]
    pre["post_period"] = (
        pd.to_datetime(pre.date)
        >= pd.to_datetime(sorted(pre.date.unique())[pre.date.nunique() // 2])
    ).astype(int)
    return trend, manual_did(pre, outcome)


def event_study(df, outcome):
    """Weekly event coefficients relative to week -1, store/date FE, clustered t intervals."""
    data = validate_panel(df, outcome)
    dates = pd.to_datetime(data.date)
    cutoff = dates[data.post_period == 1].min()
    data["event_week"] = ((dates - cutoff).dt.days // 7).astype(int)
    weeks = sorted(data.event_week.unique())
    if -1 not in weeks:
        raise ValueError("Missing reference week -1")
    terms = []
    for week in weeks:
        if week == -1:
            continue
        name = f"event_{'m' if week < 0 else 'p'}{abs(week)}"
        data[name] = data.treated_store * (data.event_week == week)
        terms.append((week, name))
    model = smf.ols(
        f"{outcome} ~ {' + '.join(n for _, n in terms)} + C(store_id) + C(date)", data=data
    ).fit(
        cov_type="cluster",
        use_t=True,
        cov_kwds={"groups": data.store_id, "use_correction": True, "df_correction": True},
    )
    ci = model.conf_int()
    return pd.DataFrame(
        [
            dict(event_week=w, estimate=model.params[n], ci_low=ci.loc[n, 0], ci_high=ci.loc[n, 1])
            for w, n in terms
        ]
    )
