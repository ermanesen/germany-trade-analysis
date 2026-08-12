"""Download, reshape, and validate World Bank indicator data."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

from .config import AnalysisConfig

LOGGER = logging.getLogger(__name__)
API_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"


def fetch_indicator(
    countries: tuple[str, ...], indicator: str, start_year: int, end_year: int
) -> pd.DataFrame:
    """Fetch one indicator, failing loudly on API or schema errors."""
    url = API_URL.format(countries=";".join(countries), indicator=indicator)
    try:
        response = requests.get(
            url,
            params={"format": "json", "per_page": 20_000, "date": f"{start_year}:{end_year}"},
            timeout=60,
        )
        response.raise_for_status()
        payload: list[Any] = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError(f"World Bank request failed for {indicator}") from exc
    if len(payload) < 2 or not isinstance(payload[1], list):
        raise RuntimeError(f"Unexpected World Bank response for {indicator}")
    rows = [
        {
            "country": item["countryiso3code"],
            "country_name": item["country"]["value"],
            "year": int(item["date"]),
            "value": item["value"],
        }
        for item in payload[1]
    ]
    return pd.DataFrame(rows)


def build_panel(config: AnalysisConfig) -> pd.DataFrame:
    """Build a balanced country-year panel and report every dropped observation."""
    expected = pd.MultiIndex.from_product(
        [config.countries, range(config.start_year, config.end_year + 1)],
        names=["country", "year"],
    ).to_frame(index=False)
    panel = expected
    country_names: pd.DataFrame | None = None
    for name, code in config.indicators.items():
        LOGGER.info("Downloading %s (%s)", name, code)
        indicator = fetch_indicator(config.countries, code, config.start_year, config.end_year)
        if indicator.duplicated(["country", "year"]).any():
            raise ValueError(f"Duplicate country-year rows in {code}")
        if country_names is None:
            country_names = indicator[["country", "country_name"]].drop_duplicates("country")
        panel = panel.merge(
            indicator[["country", "year", "value"]].rename(columns={"value": name}),
            on=["country", "year"],
            how="left",
            validate="one_to_one",
        )
    assert country_names is not None
    panel = panel.merge(country_names, on="country", how="left", validate="many_to_one")
    indicator_columns = list(config.indicators)
    missing = panel[indicator_columns].isna().any(axis=1)
    if missing.any():
        missing_pairs = panel.loc[missing, ["country", "year"]].to_dict("records")
        raise ValueError(f"Missing indicator values for {missing_pairs}")
    LOGGER.info("Validated %d of %d expected country-year rows", len(panel), len(expected))
    panel["trade_balance_pct_gdp"] = panel["exports_pct_gdp"] - panel["imports_pct_gdp"]
    panel["trade_openness_pct_gdp"] = panel["exports_pct_gdp"] + panel["imports_pct_gdp"]
    panel["export_import_coverage_pct"] = np.where(
        panel["imports_pct_gdp"].eq(0), np.nan,
        100 * panel["exports_pct_gdp"] / panel["imports_pct_gdp"],
    )
    return panel.sort_values(["country", "year"]).reset_index(drop=True)


def save_panel(panel: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(path, index=False)
    LOGGER.info("Saved %d validated rows to %s", len(panel), path)
