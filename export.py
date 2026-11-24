"""Write the scoreboard as JSON for the static website.

Usage (run by GitHub Actions, or locally):
    python -m fantasy_scoreboard.export \
        --league data/league.json --season 2026 --week 12 \
        --out site/data/scoreboard.json
"""

import argparse
import json
import os
from datetime import datetime, timezone

from .scoreboard import build_scoreboard
from .sportsdata import (
    SportsDataError,
    fetch_player_game_stats,
    fetch_scores,
    game_status_by_team,
    get_api_key,
)


def build_payload(league: dict, season: int, week: int, api_key: str) -> dict:
    stats = fetch_player_game_stats(season, week, api_key)
    scores = fetch_scores(season, week, api_key)
    owners = build_scoreboard(league, stats, game_status_by_team(scores))

    games = [
        {
            "away": g.get("AwayTeam"),
            "home": g.get("HomeTeam"),
            "status": g.get("Status", "Unknown"),
            "away_score": g.get("AwayScore"),
            "home_score": g.get("HomeScore"),
        }
        for g in scores
    ]

    return {
        "title": league.get("title", "Fantasy Scoreboard"),
        "season": season,
        "week": week,
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "all_games_final": bool(scores) and all(
            str(g.get("Status", "")).startswith("F") for g in scores
        ),
        "owners": [
            {
                "owner": o.owner,
                "points": o.points,
                "players_left": o.players_left,
                "players": [
                    {
                        "name": p.name,
                        "team": p.team,
                        "points": p.points,
                        "status": p.status,
                        "is_final": p.is_final,
                    }
                    for p in o.players
                ],
            }
            for o in owners
        ],
        "games": games,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export scoreboard JSON for the website")
    parser.add_argument("--league", required=True)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    try:
        with open(args.league, encoding="utf-8") as f:
            league = json.load(f)
        payload = build_payload(league, args.season, args.week, get_api_key())
    except (SportsDataError, OSError, json.JSONDecodeError) as err:
        raise SystemExit(f"Export failed: {err}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {args.out} ({len(payload['owners'])} owners)")


if __name__ == "__main__":
    main()
