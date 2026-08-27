from __future__ import annotations

import pandas as pd
import statsmodels.formula.api as smf


def manual_did(df: pd.DataFrame, outcome: str) -> dict:
    """Classic 2x2 difference-in-differences calculation."""
    means = df.groupby(["treated_store", "post_period"])[outcome].mean()
    control_pre = means.loc[(0, 0)]
    control_post = means.loc[(0, 1)]
    treated_pre = means.loc[(1, 0)]
    treated_post = means.loc[(1, 1)]
    treated_change = treated_post - treated_pre
    control_change = control_post - control_pre
    return {
        "control_pre": float(control_pre),
        "control_post": float(control_post),
        "treated_pre": float(treated_pre),
        "treated_post": float(treated_post),
        "treated_change": float(treated_change),
        "control_change": float(control_change),
        "did_estimate": float(treated_change - control_change),
    }


def fit_twfe_did(df: pd.DataFrame, outcome: str):
    """Two-way fixed-effects DID with standard errors clustered by store.

    Model: Y_it = alpha_i + lambda_t + beta(Treated_i x Post_t) + epsilon_it
    beta is the estimated intervention effect under the DID assumptions.
    """
    data = df.copy()
    data["did"] = data["treated_store"] * data["post_period"]
    model = smf.ols(
        f"{outcome} ~ did + C(store_id) + C(date)",
        data=data,
    ).fit(cov_type="cluster", cov_kwds={"groups": data["store_id"]})
    return model
