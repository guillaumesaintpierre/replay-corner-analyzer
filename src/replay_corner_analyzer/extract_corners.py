"""Extract corner kicks from StatsBomb event data."""

from pathlib import Path

import pandas as pd


def extract_corners(events: list[dict], match_id: int) -> pd.DataFrame:
    """Return one flat DataFrame row for each corner event."""
    rows = []

    for event in events:
        pass_data = event.get("pass", {})
        is_corner = (
            event.get("type", {}).get("name") == "Pass"
            and pass_data.get("type", {}).get("name") == "Corner"
        )
        if not is_corner:
            continue

        start_x, start_y = event["location"]
        end_x, end_y = pass_data["end_location"]
        rows.append(
            {
                "match_id": match_id,
                "event_id": event["id"],
                "index": event["index"],
                "period": event["period"],
                "timestamp": event["timestamp"],
                "minute": event["minute"],
                "second": event["second"],
                "team": event["team"]["name"],
                "player": event["player"]["name"],
                "recipient": pass_data.get("recipient", {}).get("name"),
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "pass_length": pass_data["length"],
                "pass_angle": pass_data["angle"],
                "pass_height": pass_data["height"]["name"],
                "body_part": pass_data["body_part"]["name"],
                "off_camera": event.get("off_camera", False),
            }
        )

    return pd.DataFrame(rows)


def save_corners_csv(
    corners: pd.DataFrame,
    output_path: Path | str = Path("data/processed/corners.csv"),
) -> Path:
    """Save a corner table as CSV and return its path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    corners.to_csv(destination, index=False)
    return destination
