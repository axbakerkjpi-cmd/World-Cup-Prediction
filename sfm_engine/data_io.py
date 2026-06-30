import csv
from pathlib import Path
from typing import Dict, Iterable, List

from .models import MatchInput, PredictionResult, TeamRating


def _optional_float(value: str):
    value = value.strip()
    return float(value) if value else None


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def read_teams(path: Path) -> Dict[str, TeamRating]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        return {
            row["team"]: TeamRating(
                team=row["team"],
                elo=float(row["elo"]),
                attack_strength=float(row["attack_strength"]),
                defense_weakness=float(row["defense_weakness"]),
                keeper_strength=float(row["keeper_strength"]),
                penalty_strength=float(row["penalty_strength"]),
                momentum=float(row.get("momentum") or 0.0),
            )
            for row in rows
        }


def read_matches(path: Path) -> List[MatchInput]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        return [
            MatchInput(
                match_id=row["match_id"],
                date=row["date"],
                home_team=row["home_team"],
                away_team=row["away_team"],
                neutral_site=_bool(row.get("neutral_site", "true")),
                home_odds=_optional_float(row.get("home_odds", "")),
                draw_odds=_optional_float(row.get("draw_odds", "")),
                away_odds=_optional_float(row.get("away_odds", "")),
            )
            for row in rows
        ]


def write_predictions(path: Path, predictions: Iterable[PredictionResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "match_id",
        "date",
        "home_team",
        "away_team",
        "home_lambda",
        "away_lambda",
        "home_win_prob",
        "draw_prob",
        "away_win_prob",
        "most_likely_score",
        "value_home",
        "value_draw",
        "value_away",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for prediction in predictions:
            writer.writerow({field: getattr(prediction, field) for field in fields})
