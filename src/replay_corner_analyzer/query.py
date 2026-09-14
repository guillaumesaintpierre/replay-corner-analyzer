"""Deterministic querying utilities for engineered corner data."""

import pandas as pd


def query_corners(
    corners: pd.DataFrame,
    *,
    team: str | None = None,
    side: str | None = None,
    target_zone: str | None = None,
    shot_within_10s: bool | None = None,
    min_xg: float | None = None,
    minute_min: int | None = None,
    minute_max: int | None = None,
) -> pd.DataFrame:
    """Filter corners using explicit and interpretable tactical criteria."""
    result = corners.copy()

    if team is not None:
        result = result[result["team"] == team]

    if side is not None:
        result = result[result["side"] == side]

    if target_zone is not None:
        result = result[result["target_zone"] == target_zone]

    if shot_within_10s is not None:
        result = result[
            result["shot_within_10s"] == shot_within_10s
        ]

    if min_xg is not None:
        result = result[result["xg_within_10s"] >= min_xg]

    if minute_min is not None:
        result = result[result["minute"] >= minute_min]

    if minute_max is not None:
        result = result[result["minute"] <= minute_max]

    return result.copy()
