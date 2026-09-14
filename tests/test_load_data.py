import importlib
import json


def test_download_match_events_saves_statsbomb_json(tmp_path):
    """A downloaded event list is saved under the requested match ID."""
    load_data = importlib.import_module("replay_corner_analyzer.load_data")
    expected_events = [
        {
            "id": "event-1",
            "index": 1,
            "period": 1,
            "timestamp": "00:00:00.000",
            "minute": 0,
            "second": 0,
            "type": {"id": 30, "name": "Pass"},
            "team": {"id": 904, "name": "Bayer Leverkusen"},
        }
    ]

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return expected_events

    def fake_get(url, timeout):
        assert url == (
            "https://raw.githubusercontent.com/hudl/open-data/master/"
            "data/events/3895158.json"
        )
        assert timeout == 30
        return FakeResponse()

    output_path = load_data.download_match_events(
        3895158,
        output_dir=tmp_path,
        http_get=fake_get,
    )

    assert output_path == tmp_path / "3895158.json"
    assert json.loads(output_path.read_text(encoding="utf-8")) == expected_events
