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

def test_add_target_zone_classifies_short_corner():
    corners = pd.DataFrame(
        {
            "pass_length": [4.11],
            "end_y": [40.0],
            "side": ["right"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["short_corner"]

def test_add_target_zone_classifies_central_box():
    corners = pd.DataFrame(
        {
            "pass_length": [30.0],
            "end_y": [40.0],
            "side": ["left"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["central_box"]

def test_add_target_zone_classifies_near_post_from_left_corner():
    corners = pd.DataFrame(
        {
            "pass_length": [30.0],
            "end_y": [20.0],
            "side": ["left"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["near_post"]

def test_add_target_zone_classifies_near_post_from_right_corner():
    corners = pd.DataFrame(
        {
            "pass_length": [30.0],
            "end_y": [60.0],
            "side": ["right"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["near_post"]

def test_add_target_zone_classifies_far_post_from_left_corner():
    corners = pd.DataFrame(
        {
            "pass_length": [30.0],
            "end_y": [60.0],
            "side": ["left"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["far_post"]

def test_add_target_zone_classifies_far_post_from_right_corner():
    corners = pd.DataFrame(
        {
            "pass_length": [30.0],
            "end_y": [20.0],
            "side": ["right"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["far_post"]

def test_add_target_zone_includes_lower_central_box_boundary():
    corners = pd.DataFrame(
        {
            "pass_length": [30.0],
            "end_y": [34.0],
            "side": ["left"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["central_box"]


def test_add_target_zone_includes_upper_central_box_boundary():
    corners = pd.DataFrame(
        {
            "pass_length": [30.0],
            "end_y": [46.0],
            "side": ["right"],
        }
    )

    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    featured = module.add_target_zone(corners)

    assert featured["target_zone"].tolist() == ["central_box"]
