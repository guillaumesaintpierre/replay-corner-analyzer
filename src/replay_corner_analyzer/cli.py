"""Command-line interface for deterministic REPLAY corner queries."""

import argparse
from pathlib import Path

import pandas as pd

from replay_corner_analyzer.clip_export import (
    build_clip_manifest,
    write_clip_manifest,
)
from replay_corner_analyzer.parser import (
    parse_corner_query,
)
from replay_corner_analyzer.query import (
    query_corners,
)
from replay_corner_analyzer.video_clips import (
    align_manifest_to_video,
    create_video_clips,
)


DEFAULT_DATA_PATH = Path(
    "data/processed/corners.csv"
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Search engineered football corners "
            "using natural-language queries."
        )
    )

    parser.add_argument(
        "query",
        help="Natural-language corner query.",
    )

    parser.add_argument(
        "--data",
        default=str(
            DEFAULT_DATA_PATH
        ),
        help=(
            "Path to engineered corners CSV."
        ),
    )

    parser.add_argument(
        "--export",
        help=(
            "Optional path for a JSON "
            "clip manifest."
        ),
    )

    parser.add_argument(
        "--pre-roll",
        type=int,
        default=5,
        help=(
            "Seconds before each corner."
        ),
    )

    parser.add_argument(
        "--post-roll",
        type=int,
        default=15,
        help=(
            "Seconds after each corner."
        ),
    )

    parser.add_argument(
        "--video",
        help=(
            "Optional source match video."
        ),
    )

    parser.add_argument(
        "--first-half-kickoff",
        type=float,
        help=(
            "Video timestamp in seconds "
            "of first-half kickoff."
        ),
    )

    parser.add_argument(
        "--second-half-kickoff",
        type=float,
        help=(
            "Video timestamp in seconds "
            "of second-half kickoff."
        ),
    )

    parser.add_argument(
        "--clips-dir",
        default="outputs/clips",
        help=(
            "Directory for generated MP4 clips."
        ),
    )

    return parser


def _print_filters(
    filters: dict,
) -> None:
    print("\nDetected filters:")

    if not filters:
        print("(none)")
        return

    for key, value in filters.items():
        print(
            f"{key} = {value}"
        )


def _print_results(
    results: pd.DataFrame,
) -> None:
    count = len(results)

    print()

    if count == 1:
        print("1 corner found")
    else:
        print(
            f"{count} corners found"
        )

    if count == 0:
        return

    print()

    for _, row in results.iterrows():
        minute = int(
            row["minute"]
        )

        second = int(
            row["second"]
        )

        print(
            f"{minute:02d}:{second:02d} | "
            f"{row['team']}"
        )

        print(
            f"  {row['target_zone']} | "
            f"side={row['side']} | "
            f"shot={bool(row['shot_within_10s'])} | "
            f"xG={float(row['xg_within_10s']):.3f} | "
            f"goal={bool(row['goal_within_10s'])}"
        )


def main(argv=None) -> int:
    parser = _build_parser()

    args = parser.parse_args(
        argv
    )

    data_path = Path(
        args.data
    )

    if not data_path.exists():
        parser.error(
            f"Data file not found: "
            f"{data_path}"
        )

    if args.video:
        if (
            args.first_half_kickoff is None
            or args.second_half_kickoff
            is None
        ):
            parser.error(
                "--video requires both "
                "--first-half-kickoff and "
                "--second-half-kickoff"
            )

    corners = pd.read_csv(
        data_path
    )

    teams = (
        corners["team"]
        .dropna()
        .astype(str)
        .unique()
    )

    filters = parse_corner_query(
        args.query,
        teams=teams,
    )

    results = query_corners(
        corners,
        **filters,
    )

    print(
        "\nREPLAY CORNER QUERY"
    )
    print(
        "==================="
    )

    print("\nQuery:")
    print(
        args.query
    )

    _print_filters(
        filters
    )

    _print_results(
        results
    )

    manifest = None

    if args.export or args.video:
        manifest = build_clip_manifest(
            results,
            pre_roll=args.pre_roll,
            post_roll=args.post_roll,
        )

    if args.video:
        manifest = align_manifest_to_video(
            manifest,
            first_half_kickoff=(
                args.first_half_kickoff
            ),
            second_half_kickoff=(
                args.second_half_kickoff
            ),
        )

        clips = create_video_clips(
            manifest,
            video_path=args.video,
            clips_dir=args.clips_dir,
        )

        print(
            f"\nGenerated {len(clips)} "
            "video clip(s):"
        )

        for clip in clips:
            print(
                f"  {clip}"
            )

    if args.export:
        output_path = write_clip_manifest(
            manifest,
            args.export,
        )

        print(
            "\nClip manifest exported to: "
            f"{output_path}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
