import importlib

import pandas as pd


def test_extract_corners_filters_and_flattens_corner_events():
    """Non-corner events are removed and a corner becomes one flat row."""
    module = importlib.import_module("replay_corner_analyzer.extract_corners")
    events = [
        {
            "id": "regular-pass",
            "type": {"id": 30, "name": "Pass"},
            "pass": {"type": {"id": 65, "name": "Kick Off"}},
        },
        {
            "id": "corner-1",
            "index": 447,
            "period": 1,
            "timestamp": "00:10:40.654",
            "minute": 10,
            "second": 40,
            "type": {"id": 30, "name": "Pass"},
            "team": {"id": 904, "name": "Bayer Leverkusen"},
            "player": {"id": 10336, "name": "Alejandro Grimaldo García"},
            "location": [120.0, 80.0],
            "off_camera": True,
            "pass": {
                "recipient": {"id": 40724, "name": "Florian Wirtz"},
                "length": 4.1146083,
                "angle": -2.0235748,
                "height": {"id": 1, "name": "Ground Pass"},
                "end_location": [118.2, 76.3],
                "body_part": {"id": 38, "name": "Left Foot"},
                "type": {"id": 61, "name": "Corner"},
            },
        },
    ]

    actual = module.extract_corners(events, match_id=3895158)
    expected = pd.DataFrame(
        [
            {
                "match_id": 3895158,
                "event_id": "corner-1",
                "index": 447,
                "period": 1,
                "timestamp": "00:10:40.654",
                "minute": 10,
                "second": 40,
                "team": "Bayer Leverkusen",
                "player": "Alejandro Grimaldo García",
                "recipient": "Florian Wirtz",
                "start_x": 120.0,
                "start_y": 80.0,
                "end_x": 118.2,
                "end_y": 76.3,
                "pass_length": 4.1146083,
                "pass_angle": -2.0235748,
                "pass_height": "Ground Pass",
                "body_part": "Left Foot",
                "off_camera": True,
            }
        ]
    )

    pd.testing.assert_frame_equal(actual, expected)


def test_extract_corners_handles_missing_optional_fields():
    """Corners without a recipient or off-camera flag remain usable."""
    module = importlib.import_module("replay_corner_analyzer.extract_corners")
    event = {
        "id": "corner-with-optional-fields-missing",
        "index": 900,
        "period": 2,
        "timestamp": "00:50:00.000",
        "minute": 95,
        "second": 0,
        "type": {"id": 30, "name": "Pass"},
        "team": {"id": 180, "name": "Borussia Dortmund"},
        "player": {"id": 1, "name": "Corner Taker"},
        "location": [120.0, 0.0],
        "pass": {
            "length": 25.0,
            "angle": 2.0,
            "height": {"id": 3, "name": "High Pass"},
            "end_location": [108.0, 35.0],
            "body_part": {"id": 40, "name": "Right Foot"},
            "type": {"id": 61, "name": "Corner"},
        },
    }

    corner = module.extract_corners([event], match_id=3895158).iloc[0]

    assert corner["recipient"] is None
    assert bool(corner["off_camera"]) is False


def test_save_corners_csv_creates_a_reusable_csv(tmp_path):
    """The processed table is saved without a pandas index column."""
    module = importlib.import_module("replay_corner_analyzer.extract_corners")
    corners = pd.DataFrame(
        [
            {
                "match_id": 3895158,
                "event_id": "corner-1",
                "team": "Bayer Leverkusen",
            }
        ]
    )
    output_path = tmp_path / "processed" / "corners.csv"

    saved_path = module.save_corners_csv(corners, output_path)

    assert saved_path == output_path
    pd.testing.assert_frame_equal(pd.read_csv(saved_path), corners)
