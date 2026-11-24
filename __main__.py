"""Command-line entry point.

Usage:
    python -m fantasy_scoreboard data/league.json --season 2026 --week 12
    python -m fantasy_scoreboard data/league.json --season 2026 --week 12 --watch 60
"""

import argparse
import json
import time
from datetime import datetime

from .scoreboard import build_scoreboard, format_table
from .sportsdata import (
    SportsDataError,
    fetch_player_game_stats,
    fetch_scores,
    game_status_by_team,
    get_api_key,
)


def snapshot(league: dict, season: int, week: int, api_key: str) -> tuple[str, bool]:
    """Return the printable scoreboard and whether every game this week is final."""
    stats = fetch_player_game_stats(season, week, api_key)
    scores = fetch_scores(season, week, api_key)
    status = game_status_by_team(scores)
    owners = build_scoreboard(league, stats, status)
    stamp = datetime.now().strftime("%H:%M:%S")
    text = f"{league.get('title', 'Fantasy Scoreboard')}  (updated {stamp})\n\n{format_table(owners)}"
    all_final = bool(scores) and all(str(g.get("Status", "")).startswith("F") for g in scores)
    return text, all_final


def main() -> None:
    parser = argparse.ArgumentParser(description="Fantasy scoreboard from SportsDataIO")
    parser.add_argument("league_file", help="Path to league JSON file")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument(
        "--watch",
        type=int,
        metavar="SECONDS",
        default=0,
        help="Refresh every N seconds until all games are final (0 = run once)",
    )
    args = parser.parse_args()

    with open(args.league_file, encoding="utf-8") as f:
        league = json.load(f)

    try:
        api_key = get_api_key()
        if args.watch <= 0:
            print(snapshot(league, args.season, args.week, api_key)[0])
            return
        while True:
            text, all_final = snapshot(league, args.season, args.week, api_key)
            print("\033[2J\033[H" + text)  # clear terminal and redraw
            if all_final:
                print("\nAll games final. Stopping.")
                return
            time.sleep(args.watch)
    except SportsDataError as err:
        raise SystemExit(f"Error: {err}")
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
