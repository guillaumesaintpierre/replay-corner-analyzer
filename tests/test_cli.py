import importlib

import pandas as pd


def test_cli_runs_natural_language_query(tmp_path, capsys):
    cli = importlib.import_module(
        "replay_corner_analyzer.cli"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["a", "b"],
            "minute": [51, 25],
            "second": [40, 43],
            "team": [
                "Bayer Leverkusen",
                "Bayer Leverkusen",
            ],
            "side": ["left", "left"],
            "target_zone": [
                "far_post",
                "far_post",
            ],
            "shot_within_10s": [
                True,
                True,
            ],
            "xg_within_10s": [
                0.104,
                0.120,
            ],
            "goal_within_10s": [
                False,
                False,
            ],
        }
    )

    data_path = tmp_path / "corners.csv"
    corners.to_csv(data_path, index=False)

    exit_code = cli.main(
        [
            "Montre-moi les corners au second poteau "
            "de Leverkusen après la 45e qui donnent un tir",
            "--data",
            str(data_path),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 0

    assert "Bayer Leverkusen" in output
    assert "far_post" in output
    assert "minute_min = 45" in output
    assert "1 corner found" in output
    assert "51:40" in output
    assert "xG=0.104" in output


def test_cli_handles_no_results(tmp_path, capsys):
    cli = importlib.import_module(
        "replay_corner_analyzer.cli"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["a"],
            "minute": [51],
            "second": [40],
            "team": ["Bayer Leverkusen"],
            "side": ["left"],
            "target_zone": ["far_post"],
            "shot_within_10s": [True],
            "xg_within_10s": [0.104],
            "goal_within_10s": [False],
        }
    )

    data_path = tmp_path / "corners.csv"
    corners.to_csv(data_path, index=False)

    exit_code = cli.main(
        [
            "Show me Dortmund near post corners",
            "--data",
            str(data_path),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 0
    assert "0 corners found" in output


def test_cli_exports_clip_manifest(tmp_path):
    import json

    cli = importlib.import_module(
        "replay_corner_analyzer.cli"
    )

    corners = pd.DataFrame(
        {
            "event_id": ["a"],
            "minute": [51],
            "second": [40],
            "team": ["Bayer Leverkusen"],
            "side": ["left"],
            "target_zone": ["far_post"],
            "shot_within_10s": [True],
            "xg_within_10s": [0.104],
            "goal_within_10s": [False],
        }
    )

    data_path = tmp_path / "corners.csv"
    export_path = tmp_path / "clips.json"

    corners.to_csv(
        data_path,
        index=False,
    )

    exit_code = cli.main(
        [
            "Leverkusen far post corners with a shot",
            "--data",
            str(data_path),
            "--export",
            str(export_path),
        ]
    )

    assert exit_code == 0
    assert export_path.exists()

    data = json.loads(
        export_path.read_text()
    )

    assert len(data) == 1
    assert data[0]["clip_start_seconds"] == 3095
    assert data[0]["clip_end_seconds"] == 3115
