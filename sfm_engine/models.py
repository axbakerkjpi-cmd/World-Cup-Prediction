from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class TeamRating:
    team: str
    elo: float
    attack_strength: float
    defense_weakness: float
    keeper_strength: float
    penalty_strength: float
    momentum: float = 0.0


@dataclass(frozen=True)
class MatchInput:
    match_id: str
    date: str
    home_team: str
    away_team: str
    neutral_site: bool = True
    home_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_odds: Optional[float] = None


@dataclass(frozen=True)
class PredictionResult:
    match_id: str
    date: str
    home_team: str
    away_team: str
    home_lambda: float
    away_lambda: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    most_likely_score: str
    value_home: Optional[float]
    value_draw: Optional[float]
    value_away: Optional[float]
    score_matrix: Dict[str, float]
