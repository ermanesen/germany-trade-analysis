"""Publication-ready figures."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

COLORS = {"exports": "#1261A0", "imports": "#E07A3F", "balance": "#1B7F5A", "peer": "#B7C4CE"}


def _setup() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({"figure.dpi": 120, "savefig.bbox": "tight", "axes.titleweight": "bold"})


def trade_structure(panel: pd.DataFrame, output: Path) -> None:
    _setup()
    germany = panel.loc[panel["country"].eq("DEU")]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(germany["year"], germany["exports_pct_gdp"], label="Exports", color=COLORS["exports"], lw=2.6)
    ax.plot(germany["year"], germany["imports_pct_gdp"], label="Imports", color=COLORS["imports"], lw=2.6)
    ax.fill_between(
        germany["year"], germany["imports_pct_gdp"], germany["exports_pct_gdp"],
        color=COLORS["balance"], alpha=.14, label="Trade balance",
    )
    ax.axvline(2019, color="#6B7280", ls="--", lw=1)
    ax.set(title="Germany's trade surplus narrowed after 2019", ylabel="% of GDP", xlabel="")
    ax.legend(frameon=False, ncol=3)
    sns.despine()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)


def peer_comparison(panel: pd.DataFrame, output: Path) -> None:
    _setup()
    latest = panel.loc[panel["year"].eq(panel["year"].max())].sort_values("trade_openness_pct_gdp")
    colors = [COLORS["exports"] if code == "DEU" else COLORS["peer"] for code in latest["country"]]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.barh(latest["country"], latest["trade_openness_pct_gdp"], color=colors)
    ax.set(title="Germany is less trade-open than most benchmark economies", xlabel="Exports + imports (% of GDP)", ylabel="")
    sns.despine()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)


def coefficient_plot(results: pd.DataFrame, output: Path) -> None:
    _setup()
    labels = {"lag_trade_balance": "Lagged trade balance", "lag_trade_openness": "Lagged trade openness"}
    results = results.copy()
    results["label"] = results["term"].map(labels)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    xerr = [results["estimate"] - results["ci_low"], results["ci_high"] - results["estimate"]]
    ax.errorbar(results["estimate"], results["label"], xerr=xerr, fmt="o", color=COLORS["exports"], capsize=5)
    ax.axvline(0, color="#111827", lw=1)
    ax.set(title="Only openness has a precise positive association with growth", xlabel="Coefficient (95% CI; 10-cluster t inference)", ylabel="")
    sns.despine()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)
