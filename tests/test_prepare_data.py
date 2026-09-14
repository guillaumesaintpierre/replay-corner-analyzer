import pandas as pd

from replay_corner_analyzer.prepare_data import build_corner_dataset


def test_build_corner_dataset_creates_query_ready_features():
    events = [
        {
            "id": "corner-1",
            "index": 100,
            "period": 1,
            "timestamp": "00:10:00.000",
            "minute": 10,
            "second": 0,
            "possession": 7,
            "team": {"name": "Bayer Leverkusen"},
            "player": {"name": "Corner Taker"},
            "type": {"name": "Pass"},
            "location": [120.0, 0.1],
            "pass": {
                "type": {"name": "Corner"},
                "end_location": [112.0, 12.0],
                "length": 14.34,
                "angle": 2.16,
                "height": {"name": "Ground Pass"},
                "body_part": {"name": "Right Foot"},
            },
        },
        {
            "id": "shot-1",
            "index": 105,
            "period": 1,
            "timestamp": "00:10:08.000",
            "minute": 10,
            "second": 8,
            "possession": 7,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Shot"},
            "shot": {
                "statsbomb_xg": 0.12,
                "outcome": {"name": "Saved"},
            },
        },
    ]

    result = build_corner_dataset(events, match_id=3895309)

    assert isinstance(result, pd.DataFrame)
    assert result["match_id"].tolist() == [3895309]
    assert result["side"].tolist() == ["left"]
    assert result["target_zone"].tolist() == ["short_corner"]
    assert result["shot_within_10s"].tolist() == [True]
    assert result["xg_within_10s"].tolist() == [0.12]
    assert result["goal_within_10s"].tolist() == [False]


def test_build_corner_dataset_handles_match_without_corners():
    result = build_corner_dataset([], match_id=1)

    assert result.empty
    assert {
        "side",
        "target_zone",
        "shot_within_10s",
        "xg_within_10s",
        "goal_within_10s",
    }.issubset(result.columns)
