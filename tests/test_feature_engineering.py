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


def test_add_target_zone_applies_the_validated_zone_rules():
    """Short, central, near-post and far-post corners use fixed thresholds."""
    module = importlib.import_module("replay_corner_analyzer.feature_engineering")
    corners = pd.DataFrame(
        {
            "event_id": [
                "short",
                "central-lower-bound",
                "central-upper-bound",
                "near-left",
                "near-right",
                "far-left",
                "far-right",
            ],
            "side": ["right", "left", "right", "left", "right", "left", "right"],
            "pass_length": [24.9, 25.0, 40.0, 35.0, 35.0, 40.0, 40.0],
            "end_y": [76.0, 34.0, 46.0, 33.9, 46.1, 46.1, 33.9],
        }
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == [
        "short_corner",
        "central_box",
        "central_box",
        "near_post",
        "near_post",
        "far_post",
        "far_post",
    ]
