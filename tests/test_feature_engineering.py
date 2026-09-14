import importlib

import pandas as pd


def test_add_corner_side_labels_both_sides_of_the_pitch():
    """Corners above and below midfield receive deterministic side labels."""
    module = importlib.import_module("replay_corner_analyzer.feature_engineering")
    corners = pd.DataFrame(
        {
            "event_id": ["corner-from-y-zero", "corner-from-y-eighty"],
            "start_y": [0.1, 80.0],
        }
    )

    featured = module.add_corner_side(corners)

    assert featured["side"].tolist() == ["left", "right"]
