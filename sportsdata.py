"""Minimal SportsDataIO NFL client (standard library only).

Set your key in the environment:
    export SPORTSDATAIO_KEY=your_key_here
"""

import json
import os
import urllib.error
import urllib.request

BASE_URL = "https://api.sportsdata.io/v3/nfl"


class SportsDataError(RuntimeError):
    pass


def get_api_key() -> str:
    key = os.environ.get("SPORTSDATAIO_KEY")
    if not key:
        raise SportsDataError("Set the SPORTSDATAIO_KEY environment variable.")
    return key


def _get(path: str, api_key: str):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={"Ocp-Apim-Subscription-Key": api_key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        raise SportsDataError(f"SportsDataIO returned HTTP {err.code} for {path}") from err
    except urllib.error.URLError as err:
        raise SportsDataError(f"Could not reach SportsDataIO: {err.reason}") from err


def fetch_player_game_stats(season: int, week: int, api_key: str) -> list[dict]:
    """Player box score rows for every player in a week (includes live games)."""
    return _get(f"/stats/json/PlayerGameStatsByWeek/{season}/{week}", api_key)


def fetch_scores(season: int, week: int, api_key: str) -> list[dict]:
    """Game list with status for a week. Used to tell which games are final."""
    return _get(f"/scores/json/ScoresByWeek/{season}/{week}", api_key)


def game_status_by_team(scores: list[dict]) -> dict[str, str]:
    """Map each team abbreviation to its game status string (e.g. 'Final', 'InProgress')."""
    status = {}
    for game in scores:
        for team in (game.get("HomeTeam"), game.get("AwayTeam")):
            if team:
                status[team] = game.get("Status", "Unknown")
    return status
