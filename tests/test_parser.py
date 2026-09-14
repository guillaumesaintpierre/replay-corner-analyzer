import importlib


TEAMS = [
    "Bayer Leverkusen",
    "Borussia Dortmund",
]


def load_parser():
    module = importlib.import_module(
        "replay_corner_analyzer.parser"
    )
    return module.parse_corner_query


def test_parse_french_combined_query():
    parse_corner_query = load_parser()

    filters = parse_corner_query(
        "Montre-moi les corners au second poteau de "
        "Leverkusen après la 45e qui donnent un tir",
        teams=TEAMS,
    )

    assert filters == {
        "team": "Bayer Leverkusen",
        "target_zone": "far_post",
        "shot_within_10s": True,
        "minute_min": 45,
    }


def test_parse_english_query():
    parse_corner_query = load_parser()

    filters = parse_corner_query(
        "Show me Dortmund near post corners before the 70th minute",
        teams=TEAMS,
    )

    assert filters == {
        "team": "Borussia Dortmund",
        "target_zone": "near_post",
        "minute_max": 70,
    }


def test_parse_short_corner_without_shot():
    parse_corner_query = load_parser()

    filters = parse_corner_query(
        "Corners courts de Leverkusen sans tir",
        teams=TEAMS,
    )

    assert filters == {
        "team": "Bayer Leverkusen",
        "target_zone": "short_corner",
        "shot_within_10s": False,
    }


def test_parse_central_box():
    parse_corner_query = load_parser()

    filters = parse_corner_query(
        "Corners dans la zone centrale",
        teams=TEAMS,
    )

    assert filters == {
        "target_zone": "central_box",
    }


def test_parse_explicit_minimum_xg():
    parse_corner_query = load_parser()

    filters = parse_corner_query(
        "Leverkusen corners with xG >= 0.05",
        teams=TEAMS,
    )

    assert filters == {
        "team": "Bayer Leverkusen",
        "min_xg": 0.05,
    }


def test_parse_query_with_no_known_filter_returns_empty_dict():
    parse_corner_query = load_parser()

    filters = parse_corner_query(
        "Montre-moi quelque chose",
        teams=TEAMS,
    )

    assert filters == {}
