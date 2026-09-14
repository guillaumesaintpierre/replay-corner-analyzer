import importlib
import json

import pandas as pd


def test_build_clip_manifest_adds_pre_and_post_roll():
    module = importlib.import_module(
        "replay_corner_analyzer.clip_export"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "minute": [51],
            "second": [40],
            "team": ["Bayer Leverkusen"],
            "target_zone": ["far_post"],
            "xg_within_10s": [0.104],
        }
    )

    manifest = module.build_clip_manifest(
        corners,
        pre_roll=5,
        post_roll=15,
    )

    assert len(manifest) == 1
    assert manifest[0]["clip_start_seconds"] == 3095
    assert manifest[0]["clip_end_seconds"] == 3115
    assert manifest[0]["target_zone"] == "far_post"


def test_build_clip_manifest_never_starts_before_zero():
    module = importlib.import_module(
        "replay_corner_analyzer.clip_export"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "minute": [0],
            "second": [3],
            "team": ["Bayer Leverkusen"],
            "target_zone": ["short_corner"],
            "xg_within_10s": [0.0],
        }
    )

    manifest = module.build_clip_manifest(
        corners,
        pre_roll=5,
        post_roll=15,
    )

    assert manifest[0]["clip_start_seconds"] == 0
    assert manifest[0]["clip_end_seconds"] == 18


def test_export_clip_manifest_writes_json(tmp_path):
    module = importlib.import_module(
        "replay_corner_analyzer.clip_export"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["corner-1"],
            "minute": [51],
            "second": [40],
            "team": ["Bayer Leverkusen"],
            "target_zone": ["far_post"],
            "xg_within_10s": [0.104],
        }
    )

    output_path = tmp_path / "clips.json"

    module.export_clip_manifest(
        corners,
        output_path,
        pre_roll=5,
        post_roll=15,
    )

    data = json.loads(output_path.read_text())

    assert len(data) == 1
    assert data[0]["event_id"] == "corner-1"
    assert data[0]["clip_start_seconds"] == 3095
    assert data[0]["clip_end_seconds"] == 3115
