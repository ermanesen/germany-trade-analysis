import json


def test_notebook_is_executed_and_documented(project_root):
    notebook = json.loads((project_root / "notebooks/analysis.ipynb").read_text(encoding="utf-8"))
    code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    markdown = [cell for cell in notebook["cells"] if cell["cell_type"] == "markdown"]
    assert len(markdown) >= 6
    assert code and all(cell["execution_count"] is not None for cell in code)
    assert not any(
        output.get("output_type") == "error"
        for cell in code
        for output in cell.get("outputs", [])
    )


def test_figures_are_not_empty(project_root):
    for name in ("germany_trade_structure.svg", "peer_openness_2024.svg", "growth_model_coefficients.svg"):
        assert (project_root / "figures" / name).stat().st_size > 1_000
