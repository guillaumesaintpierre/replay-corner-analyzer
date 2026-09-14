import importlib
import pandas as pd


def test_add_shot_within_10s_detects_same_possession_shot():
    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "index": [100],
            "period": [1],
            "timestamp": ["00:10:40.000"],
            "team": ["Bayer Leverkusen"],
        }
    )

    events = [
        {
            "id": "corner-1",
            "index": 100,
            "period": 1,
            "timestamp": "00:10:40.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Pass"},
        },
        {
            "id": "shot-1",
            "index": 110,
            "period": 1,
            "timestamp": "00:10:48.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Shot"},
        },
    ]

    featured = module.add_shot_within_10s(corners, events)

    assert featured["shot_within_10s"].tolist() == [True]


def test_add_shot_within_10s_ignores_new_possession():
    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "index": [100],
            "period": [1],
            "timestamp": ["00:10:40.000"],
            "team": ["Bayer Leverkusen"],
        }
    )

    events = [
        {
            "id": "corner-1",
            "index": 100,
            "period": 1,
            "timestamp": "00:10:40.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Pass"},
        },
        {
            "id": "shot-1",
            "index": 110,
            "period": 1,
            "timestamp": "00:10:48.000",
            "possession": 43,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Shot"},
        },
    ]

    featured = module.add_shot_within_10s(corners, events)

    assert featured["shot_within_10s"].tolist() == [False]


def test_add_shot_within_10s_ignores_opponent_and_late_shots():
    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "index": [100],
            "period": [1],
            "timestamp": ["00:10:40.000"],
            "team": ["Bayer Leverkusen"],
        }
    )

    events = [
        {
            "id": "corner-1",
            "index": 100,
            "period": 1,
            "timestamp": "00:10:40.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Pass"},
        },
        {
            "id": "shot-opponent",
            "index": 105,
            "period": 1,
            "timestamp": "00:10:45.000",
            "possession": 42,
            "team": {"name": "Borussia Dortmund"},
            "type": {"name": "Shot"},
        },
        {
            "id": "shot-late",
            "index": 120,
            "period": 1,
            "timestamp": "00:10:51.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Shot"},
        },
    ]

    featured = module.add_shot_within_10s(corners, events)

    assert featured["shot_within_10s"].tolist() == [False]


def test_add_shot_within_10s_aggregates_xg_and_detects_goal():
    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "index": [100],
            "period": [1],
            "timestamp": ["00:10:40.000"],
            "team": ["Bayer Leverkusen"],
        }
    )

    events = [
        {
            "id": "corner-1",
            "index": 100,
            "period": 1,
            "timestamp": "00:10:40.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Pass"},
        },
        {
            "id": "shot-1",
            "index": 110,
            "period": 1,
            "timestamp": "00:10:45.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Shot"},
            "shot": {
                "statsbomb_xg": 0.08,
                "outcome": {"name": "Saved"},
            },
        },
        {
            "id": "shot-2",
            "index": 115,
            "period": 1,
            "timestamp": "00:10:49.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Shot"},
            "shot": {
                "statsbomb_xg": 0.31,
                "outcome": {"name": "Goal"},
            },
        },
    ]

    featured = module.add_shot_within_10s(corners, events)

    assert featured["shot_within_10s"].tolist() == [True]
    assert abs(featured.loc[0, "xg_within_10s"] - 0.39) < 1e-9
    assert featured["goal_within_10s"].tolist() == [True]


def test_add_shot_within_10s_returns_zero_xg_and_no_goal_without_shot():
    module = importlib.import_module(
        "replay_corner_analyzer.feature_engineering"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "index": [100],
            "period": [1],
            "timestamp": ["00:10:40.000"],
            "team": ["Bayer Leverkusen"],
        }
    )

    events = [
        {
            "id": "corner-1",
            "index": 100,
            "period": 1,
            "timestamp": "00:10:40.000",
            "possession": 42,
            "team": {"name": "Bayer Leverkusen"},
            "type": {"name": "Pass"},
        }
    ]

    featured = module.add_shot_within_10s(corners, events)

    assert featured["shot_within_10s"].tolist() == [False]
    assert featured["xg_within_10s"].tolist() == [0.0]
    assert featured["goal_within_10s"].tolist() == [False]
