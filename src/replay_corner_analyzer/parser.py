"""Deterministic natural-language parsing for corner queries."""

import re
import unicodedata
from collections.abc import Iterable


def _normalize(text: str) -> str:
    """Normalize text for deterministic keyword matching."""
    text = text.lower()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = text.replace("-", " ")

    return " ".join(text.split())


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(
        _normalize(phrase) in text
        for phrase in phrases
    )


def _detect_team(
    text: str,
    teams: Iterable[str] | None,
) -> str | None:
    if teams is None:
        return None

    candidates = []

    for team in teams:
        normalized_team = _normalize(str(team))

        aliases = {normalized_team}

        for token in normalized_team.split():
            if len(token) >= 5:
                aliases.add(token)

        for alias in aliases:
            if alias in text:
                candidates.append(
                    (len(alias), str(team))
                )

    if not candidates:
        return None

    candidates.sort(reverse=True)

    return candidates[0][1]


def _extract_minute(
    text: str,
    patterns: list[str],
) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))

    return None


def _extract_min_xg(text: str) -> float | None:
    patterns = [
        r"\bxg\s*>=\s*(\d+(?:[.,]\d+)?)",
        r"\bxg\s+above\s+(\d+(?:[.,]\d+)?)",
        r"\bxg\s+over\s+(\d+(?:[.,]\d+)?)",
        r"\bxg\s+superieur\s+a\s+(\d+(?:[.,]\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return float(
                match.group(1).replace(",", ".")
            )

    return None


def parse_corner_query(
    text: str,
    *,
    teams: Iterable[str] | None = None,
) -> dict:
    """Translate a simple FR/EN corner request into explicit filters."""
    normalized = _normalize(text)

    filters = {}

    team = _detect_team(
        normalized,
        teams,
    )

    if team is not None:
        filters["team"] = team

    zone_synonyms = {
        "far_post": [
            "second poteau",
            "deuxieme poteau",
            "2e poteau",
            "far post",
        ],
        "near_post": [
            "premier poteau",
            "1er poteau",
            "near post",
        ],
        "short_corner": [
            "corner court",
            "corners courts",
            "short corner",
            "short corners",
        ],
        "central_box": [
            "zone centrale",
            "central box",
            "centre de la surface",
            "centre surface",
        ],
    }

    for zone, phrases in zone_synonyms.items():
        if _contains_any(normalized, phrases):
            filters["target_zone"] = zone
            break

    negative_shot_phrases = [
        "sans tir",
        "sans tirs",
        "without shot",
        "without a shot",
        "no shot",
    ]

    positive_shot_phrases = [
        "avec tir",
        "avec un tir",
        "donnent un tir",
        "donne un tir",
        "menent a un tir",
        "mene a un tir",
        "produisent un tir",
        "produit un tir",
        "with shot",
        "with a shot",
        "lead to a shot",
        "leading to a shot",
    ]

    if _contains_any(
        normalized,
        negative_shot_phrases,
    ):
        filters["shot_within_10s"] = False

    elif _contains_any(
        normalized,
        positive_shot_phrases,
    ):
        filters["shot_within_10s"] = True

    minute_min = _extract_minute(
        normalized,
        [
            r"\bapres(?: la)?\s+(\d{1,3})(?:e|eme|er)?\b",
            r"\ba partir de(?: la)?\s+(\d{1,3})(?:e|eme|er)?\b",
            r"\bafter(?: the)?\s+(\d{1,3})(?:st|nd|rd|th)?\b",
        ],
    )

    if minute_min is not None:
        filters["minute_min"] = minute_min

    minute_max = _extract_minute(
        normalized,
        [
            r"\bavant(?: la)?\s+(\d{1,3})(?:e|eme|er)?\b",
            r"\bbefore(?: the)?\s+(\d{1,3})(?:st|nd|rd|th)?\b",
        ],
    )

    if minute_max is not None:
        filters["minute_max"] = minute_max

    min_xg = _extract_min_xg(normalized)

    if min_xg is not None:
        filters["min_xg"] = min_xg

    side_synonyms = {
        "left": [
            "cote gauche",
            "left side",
        ],
        "right": [
            "cote droit",
            "right side",
        ],
    }

    for side, phrases in side_synonyms.items():
        if _contains_any(normalized, phrases):
            filters["side"] = side
            break

    return filters
