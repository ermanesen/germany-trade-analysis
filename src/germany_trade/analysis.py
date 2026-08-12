"""Descriptive and panel-model analysis."""

from __future__ import annotations

import pandas as pd
from linearmodels.panel import PanelOLS
from scipy.stats import t as student_t


def prepare_model_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Lag trade variables so the accounting identity is never used as a regression."""
    data = panel.sort_values(["country", "year"]).copy()
    by_country = data.groupby("country", observed=True)
    data["lag_trade_balance"] = by_country["trade_balance_pct_gdp"].shift(1)
    data["lag_trade_openness"] = by_country["trade_openness_pct_gdp"].shift(1)
    return data.dropna(subset=["gdp_growth", "lag_trade_balance", "lag_trade_openness"])


def fit_growth_model(panel: pd.DataFrame):
    """Estimate a two-way fixed-effects association model with clustered errors."""
    data = prepare_model_data(panel).set_index(["country", "year"])
    model = PanelOLS.from_formula(
        "gdp_growth ~ 1 + lag_trade_balance + lag_trade_openness + EntityEffects + TimeEffects",
        data=data,
        drop_absorbed=True,
    )
    result = model.fit(cov_type="clustered", cluster_entity=True, group_debias=True)
    return result


def model_table(result) -> pd.DataFrame:
    """Return focal estimates using conservative small-cluster t inference."""
    cluster_df = int(result.entity_info.total - 1)
    critical = student_t.ppf(0.975, cluster_df)
    rows = []
    for term in ("lag_trade_balance", "lag_trade_openness"):
        estimate = float(result.params[term])
        standard_error = float(result.std_errors[term])
        statistic = estimate / standard_error
        rows.append(
            {
                "term": term,
                "estimate": estimate,
                "std_error": standard_error,
                "t_stat": statistic,
                "p_value_small_cluster": float(2 * student_t.sf(abs(statistic), cluster_df)),
                "ci_low": estimate - critical * standard_error,
                "ci_high": estimate + critical * standard_error,
                "observations": int(result.nobs),
                "countries": cluster_df + 1,
                "r_squared_within": float(result.rsquared_within),
            }
        )
    return pd.DataFrame(rows)


def snapshot_table(panel: pd.DataFrame, focus_country: str = "DEU") -> pd.DataFrame:
    latest_year = int(panel["year"].max())
    current = panel.loc[panel["year"].eq(latest_year)].copy()
    current["balance_rank"] = current["trade_balance_pct_gdp"].rank(ascending=False, method="min")
    current["openness_rank"] = current["trade_openness_pct_gdp"].rank(ascending=False, method="min")
    current["growth_rank"] = current["gdp_growth"].rank(ascending=False, method="min")
    return current.sort_values("trade_openness_pct_gdp", ascending=False)
