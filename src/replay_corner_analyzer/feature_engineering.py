"""Create interpretable tactical features for corner kicks."""

import pandas as pd


SHORT_CORNER_MAX_LENGTH = 25.0
CENTRAL_BOX_MIN_Y = 34.0
CENTRAL_BOX_MAX_Y = 46.0


def add_corner_side(corners: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a deterministic left/right corner side."""
    featured = corners.copy()
    featured["side"] = featured["start_y"].map(
        lambda start_y: "left" if start_y < 40 else "right"
    )
    return featured


def _classify_target_zone(corner: pd.Series) -> str:
    if corner["pass_length"] < SHORT_CORNER_MAX_LENGTH:
        return "short_corner"

    if CENTRAL_BOX_MIN_Y <= corner["end_y"] <= CENTRAL_BOX_MAX_Y:
        return "central_box"

    targets_near_post = (
        corner["side"] == "left" and corner["end_y"] < CENTRAL_BOX_MIN_Y
    ) or (
        corner["side"] == "right" and corner["end_y"] > CENTRAL_BOX_MAX_Y
    )
    return "near_post" if targets_near_post else "far_post"


def add_target_zone(corners: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with an interpretable deterministic target zone."""
    featured = corners.copy()
    featured["target_zone"] = featured.apply(_classify_target_zone, axis=1)
    return featured
