"""Build JSON-ready clip windows from queried corner events."""

import json
from pathlib import Path

import pandas as pd


def build_clip_manifest(
    corners: pd.DataFrame,
    *,
    pre_roll: int = 5,
    post_roll: int = 15,
) -> list[dict]:
    """Convert queried corners into deterministic match-clock clip windows."""
    clips = []

    for _, row in corners.iterrows():
        event_time = (
            int(row["minute"]) * 60
            + int(row["second"])
        )

        clip_start = max(
            0,
            event_time - pre_roll,
        )

        clip_end = (
            event_time + post_roll
        )

        clip = {
            "event_id": str(
                row["event_id"]
            ),
            "team": str(
                row["team"]
            ),
            "minute": int(
                row["minute"]
            ),
            "second": int(
                row["second"]
            ),
            "event_time_seconds": (
                event_time
            ),
            "clip_start_seconds": (
                clip_start
            ),
            "clip_end_seconds": (
                clip_end
            ),
            "target_zone": str(
                row["target_zone"]
            ),
            "xg_within_10s": float(
                row.get(
                    "xg_within_10s",
                    0.0,
                )
            ),
        }

        if "period" in row.index:
            clip["period"] = int(
                row["period"]
            )

        if "timestamp" in row.index:
            clip["timestamp"] = str(
                row["timestamp"]
            )

        if "shot_within_10s" in row.index:
            clip["shot_within_10s"] = bool(
                row["shot_within_10s"]
            )

        if "goal_within_10s" in row.index:
            clip["goal_within_10s"] = bool(
                row["goal_within_10s"]
            )

        clips.append(clip)

    return clips


def write_clip_manifest(
    manifest: list[dict],
    output_path,
) -> Path:
    """Write an already-built manifest to JSON."""
    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def export_clip_manifest(
    corners: pd.DataFrame,
    output_path,
    *,
    pre_roll: int = 5,
    post_roll: int = 15,
) -> Path:
    """Build and write queried corner clip windows to JSON."""
    manifest = build_clip_manifest(
        corners,
        pre_roll=pre_roll,
        post_roll=post_roll,
    )

    return write_clip_manifest(
        manifest,
        output_path,
    )
