"""Run the complete project from the repository root."""

import argparse
from pathlib import Path

from germany_trade.pipeline import configure_logging, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Download the latest World Bank values")
    args = parser.parse_args()
    configure_logging()
    run(Path(__file__).resolve().parents[1], refresh=args.refresh)


if __name__ == "__main__":
    main()
