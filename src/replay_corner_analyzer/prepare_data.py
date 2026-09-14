"""Prepare an engineered corner dataset from StatsBomb Open Data."""

import argparse
import json
from pathlib import Path

import pandas as pd

from replay_corner_analyzer.extract_corners import (
    extract_corners,
    save_corners_csv,
)
from replay_corner_analyzer.feature_engineering import (
    add_corner_side,
    add_shot_within_10s,
    add_target_zone,
)
from replay_corner_analyzer.load_data import download_match_events


DEFAULT_OUTPUT_PATH = Path("data/processed/corners.csv")
DEFAULT_RAW_DIR = Path("data/raw")


def build_corner_dataset(
    events: list[dict],
    match_id: int,
) -> pd.DataFrame:
    """Extract corners and add every feature required by the query CLI."""
    corners = extract_corners(events, match_id)

    if corners.empty:
        return corners.assign(
            side=pd.Series(dtype="object"),
            target_zone=pd.Series(dtype="object"),
            shot_within_10s=pd.Series(dtype="bool"),
            xg_within_10s=pd.Series(dtype="float64"),
            goal_within_10s=pd.Series(dtype="bool"),
        )

    featured = add_corner_side(corners)
    featured = add_target_zone(featured)
    featured = add_shot_within_10s(featured, events)
    return featured


def prepare_match(
    match_id: int,
    *,
    raw_dir: Path | str = DEFAULT_RAW_DIR,
    output_path: Path | str = DEFAULT_OUTPUT_PATH,
) -> pd.DataFrame:
    """Download one match, engineer its corners, and save the result."""
    raw_path = download_match_events(
        match_id,
        output_dir=raw_dir,
    )
    events = json.loads(
        raw_path.read_text(encoding="utf-8")
    )

    corners = build_corner_dataset(events, match_id)
    save_corners_csv(corners, output_path)
    return corners


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Download a StatsBomb match and build an engineered corner CSV."
        )
    )
    parser.add_argument(
        "match_id",
        type=int,
        help="StatsBomb Open Data match identifier.",
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Directory used for the downloaded event JSON.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Destination of the engineered corner CSV.",
    )
    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    corners = prepare_match(
        args.match_id,
        raw_dir=args.raw_dir,
        output_path=args.output,
    )
    print(
        f"Prepared {len(corners)} corners in {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
