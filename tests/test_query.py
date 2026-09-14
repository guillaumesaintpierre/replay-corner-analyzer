import importlib

import pandas as pd


def load_query_corners():
    module = importlib.import_module("replay_corner_analyzer.query")
    return module.query_corners


def sample_corners():
    return pd.DataFrame(
        {
            "event_id": ["a", "b", "c", "d"],
            "team": [
                "Bayer Leverkusen",
                "Bayer Leverkusen",
                "Bayer Leverkusen",
                "Borussia Dortmund",
            ],
            "side": ["left", "left", "right", "right"],
            "target_zone": [
                "far_post",
                "far_post",
                "short_corner",
                "far_post",
            ],
            "shot_within_10s": [True, False, True, True],
            "xg_within_10s": [0.12, 0.00, 0.07, 0.20],
            "minute": [51, 25, 87, 65],
        }
    )


def test_query_corners_combines_filters():
    query_corners = load_query_corners()
    corners = sample_corners()

    result = query_corners(
        corners,
        team="Bayer Leverkusen",
        target_zone="far_post",
        shot_within_10s=True,
    )

    assert result["event_id"].tolist() == ["a"]


def test_query_corners_filters_xg_and_minutes():
    query_corners = load_query_corners()
    corners = sample_corners()

    result = query_corners(
        corners,
        min_xg=0.10,
        minute_min=45,
        minute_max=70,
    )

    assert result["event_id"].tolist() == ["a", "d"]


def test_query_corners_filters_side():
    query_corners = load_query_corners()
    corners = sample_corners()

    result = query_corners(
        corners,
        side="right",
    )

    assert result["event_id"].tolist() == ["c", "d"]


def test_query_corners_without_filters_returns_all_rows():
    query_corners = load_query_corners()
    corners = sample_corners()

    result = query_corners(corners)

    assert result["event_id"].tolist() == ["a", "b", "c", "d"]
    assert result is not corners
