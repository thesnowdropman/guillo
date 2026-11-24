"""Build a scoreboard from roster data and SportsDataIO stat rows.

No projections or predictions: points are the sum of scored stats so far,
and each player is marked final or not based on their game's status.
"""

from dataclasses import dataclass, field

from .scoring import DEFAULT_RULES, ScoringRules, score_stat_line

# SportsDataIO uses "Final", "F/OT", etc. for completed games.
FINAL_PREFIX = "F"


@dataclass
class PlayerLine:
    name: str
    team: str
    points: float
    status: str
    is_final: bool


@dataclass
class OwnerScore:
    owner: str
    points: float = 0.0
    players: list[PlayerLine] = field(default_factory=list)

    @property
    def players_left(self) -> int:
        return sum(1 for p in self.players if not p.is_final)


def _stat_line(row: dict) -> dict:
    """Pull the fields used for scoring out of a SportsDataIO player row."""
    return {
        "receptions": row.get("Receptions") or 0,
        "passing_yards": row.get("PassingYards") or 0,
        "rushing_yards": row.get("RushingYards") or 0,
        "receiving_yards": row.get("ReceivingYards") or 0,
        "passing_tds": row.get("PassingTouchdowns") or 0,
        "rushing_tds": row.get("RushingTouchdowns") or 0,
        "receiving_tds": row.get("ReceivingTouchdowns") or 0,
    }


def build_scoreboard(
    league: dict,
    stat_rows: list[dict],
    team_status: dict[str, str],
    rules: ScoringRules = DEFAULT_RULES,
) -> list[OwnerScore]:
    """Score every owner's roster.

    league: {"teams": [{"owner": str, "players": [{"name": str, "team": str}, ...]}]}
    stat_rows: SportsDataIO PlayerGameStatsByWeek rows
    team_status: {"CIN": "Final", ...} from game_status_by_team()
    """
    rows_by_name = {row.get("Name"): row for row in stat_rows if row.get("Name")}

    results = []
    for team_entry in league["teams"]:
        owner_score = OwnerScore(owner=team_entry["owner"])
        for player in team_entry["players"]:
            name, team = player["name"], player["team"]
            row = rows_by_name.get(name)
            points = score_stat_line(_stat_line(row), rules) if row else 0.0
            status = team_status.get(team, "Unknown")
            owner_score.players.append(
                PlayerLine(
                    name=name,
                    team=team,
                    points=points,
                    status=status,
                    is_final=status.startswith(FINAL_PREFIX),
                )
            )
            owner_score.points += points
        owner_score.points = round(owner_score.points, 2)
        results.append(owner_score)

    return sorted(results, key=lambda o: o.points, reverse=True)


def format_table(scores: list[OwnerScore]) -> str:
    lines = [f"{'Owner':<14}{'Points':>10}{'Players left':>15}"]
    for s in scores:
        lines.append(f"{s.owner:<14}{s.points:>10.2f}{s.players_left:>15}")
    return "\n".join(lines)
