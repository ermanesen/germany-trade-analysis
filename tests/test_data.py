import numpy as np
import pandas as pd


def test_panel_is_complete_and_unique(project_root):
    panel = pd.read_csv(project_root / "data/processed/eu_trade_panel.csv")
    assert len(panel) == 250
    assert panel["country"].nunique() == 10
    assert panel["year"].nunique() == 25
    assert not panel.duplicated(["country", "year"]).any()
    assert not panel.isna().any().any()


def test_accounting_indicators_are_correct(project_root):
    panel = pd.read_csv(project_root / "data/processed/eu_trade_panel.csv")
    np.testing.assert_allclose(
        panel["trade_balance_pct_gdp"], panel["exports_pct_gdp"] - panel["imports_pct_gdp"]
    )
    np.testing.assert_allclose(
        panel["trade_openness_pct_gdp"], panel["exports_pct_gdp"] + panel["imports_pct_gdp"]
    )
