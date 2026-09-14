"""Download raw StatsBomb event data."""

import json
from pathlib import Path

import requests


STATSBOMB_EVENTS_URL = (
    "https://raw.githubusercontent.com/hudl/open-data/master/"
    "data/events/{match_id}.json"
)


def download_match_events(
    match_id: int,
    output_dir: Path | str = Path("data/raw"),
    http_get=requests.get,
) -> Path:
    """Download one match's events and return the saved JSON path."""
    url = STATSBOMB_EVENTS_URL.format(match_id=match_id)
    response = http_get(url, timeout=30)
    response.raise_for_status()
    events = response.json()

    output_directory = Path(output_dir)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"{match_id}.json"
    output_path.write_text(
        json.dumps(events, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return output_path
