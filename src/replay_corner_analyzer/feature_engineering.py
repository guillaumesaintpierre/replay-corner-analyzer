"""Create interpretable tactical features for corner kicks."""

import pandas as pd


def add_corner_side(corners: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a deterministic left/right corner side."""
    featured = corners.copy()

    featured["side"] = featured["start_y"].map(
        lambda start_y: "left" if start_y < 40 else "right"
    )

    return featured


def add_target_zone(corners: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a deterministic target zone for each corner."""
    featured = corners.copy()

    def classify_corner(row):
        if row["pass_length"] < 25:
            return "short_corner"

        if 34 <= row["end_y"] <= 46:
            return "central_box"

        if row["side"] == "left" and row["end_y"] < 34:
            return "near_post"

        if row["side"] == "right" and row["end_y"] > 46:
            return "near_post"

        return "far_post"

    featured["target_zone"] = featured.apply(classify_corner, axis=1)

    return featured




def add_shot_within_10s(
    corners: pd.DataFrame,
    events: list[dict],
    window_seconds: float = 10.0,
) -> pd.DataFrame:
    """Add shot, xG and goal outcomes created by a corner within 10 seconds."""
    featured = corners.copy()

    events_by_id = {
        event.get("id"): event
        for event in events
        if event.get("id") is not None
    }

    events_by_index = {
        event.get("index"): event
        for event in events
        if event.get("index") is not None
    }

    shots = []

    for event in events:
        if event.get("type", {}).get("name") != "Shot":
            continue

        timestamp = event.get("timestamp")

        if timestamp is None:
            continue

        shot_data = event.get("shot", {})

        shots.append(
            {
                "index": event.get("index"),
                "period": event.get("period"),
                "possession": event.get("possession"),
                "timestamp_seconds": pd.to_timedelta(
                    timestamp
                ).total_seconds(),
                "team": event.get("team", {}).get("name"),
                "xg": float(shot_data.get("statsbomb_xg", 0.0) or 0.0),
                "goal": (
                    shot_data.get("outcome", {}).get("name") == "Goal"
                ),
            }
        )

    def corner_outcome(row):
        corner_event = None

        if "event_id" in row.index:
            corner_event = events_by_id.get(row["event_id"])

        if corner_event is None:
            corner_event = events_by_index.get(row["index"])

        if corner_event is None:
            return pd.Series(
                {
                    "shot_within_10s": False,
                    "xg_within_10s": 0.0,
                    "goal_within_10s": False,
                }
            )

        corner_possession = corner_event.get("possession")

        if corner_possession is None:
            return pd.Series(
                {
                    "shot_within_10s": False,
                    "xg_within_10s": 0.0,
                    "goal_within_10s": False,
                }
            )

        corner_time = pd.to_timedelta(
            row["timestamp"]
        ).total_seconds()

        qualified_shots = []

        for shot in shots:
            if shot["period"] != row["period"]:
                continue

            if shot["index"] <= row["index"]:
                continue

            if shot["team"] != row["team"]:
                continue

            if shot["possession"] != corner_possession:
                continue

            delta = shot["timestamp_seconds"] - corner_time

            if 0 <= delta <= window_seconds:
                qualified_shots.append(shot)

        return pd.Series(
            {
                "shot_within_10s": len(qualified_shots) > 0,
                "xg_within_10s": sum(
                    shot["xg"] for shot in qualified_shots
                ),
                "goal_within_10s": any(
                    shot["goal"] for shot in qualified_shots
                ),
            }
        )

    outcome = featured.apply(corner_outcome, axis=1)

    featured[
        [
            "shot_within_10s",
            "xg_within_10s",
            "goal_within_10s",
        ]
    ] = outcome[
        [
            "shot_within_10s",
            "xg_within_10s",
            "goal_within_10s",
        ]
    ]

    return featured
