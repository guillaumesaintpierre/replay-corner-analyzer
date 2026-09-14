"""Create interpretable tactical features for corner kicks."""

import pandas as pd


def add_corner_side(corners: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a deterministic left/right corner side."""
    featured = corners.copy()
    featured["side"] = featured["start_y"].map(
        lambda start_y: "left" if start_y < 40 else "right"
    )
    return featured
