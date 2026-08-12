"""Configuration loading."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class AnalysisConfig:
    start_year: int
    end_year: int
    focus_country: str
    countries: tuple[str, ...]
    indicators: dict[str, str]


def load_config(path: Path) -> AnalysisConfig:
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    return AnalysisConfig(
        start_year=int(raw["start_year"]),
        end_year=int(raw["end_year"]),
        focus_country=str(raw["focus_country"]),
        countries=tuple(raw["countries"]),
        indicators=dict(raw["indicators"]),
    )
