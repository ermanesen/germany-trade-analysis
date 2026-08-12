import pandas as pd

from germany_trade.analysis import fit_growth_model, model_table, prepare_model_data


def test_model_uses_lagged_trade_exposure_not_accounting_tautology(project_root):
    panel = pd.read_csv(project_root / "data/processed/eu_trade_panel.csv")
    model_data = prepare_model_data(panel)
    assert len(model_data) == 240
    assert model_data["country"].nunique() == 10
    result = fit_growth_model(panel)
    assert result.dependent.vars == ["gdp_growth"]
    assert set(result.params.index) >= {"lag_trade_balance", "lag_trade_openness"}
    assert not {"exports_pct_gdp", "imports_pct_gdp"}.issubset(result.params.index)


def test_model_reproduces_benchmark_estimates(project_root):
    panel = pd.read_csv(project_root / "data/processed/eu_trade_panel.csv")
    table = model_table(fit_growth_model(panel)).set_index("term")
    assert table.loc["lag_trade_balance", "estimate"] == pytest.approx(-0.055, abs=0.005)
    assert table.loc["lag_trade_openness", "estimate"] == pytest.approx(0.0308, abs=0.005)
    assert (table["observations"] == 240).all()
    assert (table["countries"] == 10).all()


import pytest
