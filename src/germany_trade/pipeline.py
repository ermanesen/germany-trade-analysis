"""End-to-end analysis pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .analysis import fit_growth_model, model_table, snapshot_table
from .config import load_config
from .data import build_panel, save_panel
from .visualize import coefficient_plot, peer_comparison, trade_structure


def run(root: Path, refresh: bool = False) -> None:
    config = load_config(root / "config" / "analysis.toml")
    panel_path = root / "data" / "processed" / "eu_trade_panel.csv"
    panel = build_panel(config) if refresh or not panel_path.exists() else pd.read_csv(panel_path)
    save_panel(panel, panel_path)

    result = fit_growth_model(panel)
    estimates = model_table(result)
    tables = root / "reports" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    estimates.to_csv(tables / "growth_model.csv", index=False)
    snapshot_table(panel, config.focus_country).to_csv(tables / "latest_snapshot.csv", index=False)
    (tables / "growth_model.txt").write_text(str(result.summary), encoding="utf-8")

    figures = root / "figures"
    trade_structure(panel, figures / "germany_trade_structure.png")
    peer_comparison(panel, figures / "peer_openness_2024.png")
    coefficient_plot(estimates, figures / "growth_model_coefficients.png")


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
