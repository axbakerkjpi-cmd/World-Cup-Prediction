from typing import Optional

from .elo import elo_goal_factor, home_advantage_elo
from .models import MatchInput, PredictionResult, TeamRating
from .poisson import most_likely_score, outcome_probabilities, score_matrix


def _clamp(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))


def _value_index(probability: float, odds: Optional[float]) -> Optional[float]:
    if odds is None:
        return None
    return probability * odds - 1.0


def predict_match(
    match: MatchInput,
    home: TeamRating,
    away: TeamRating,
    base_home_goals: float = 1.36,
    base_away_goals: float = 1.18,
    matrix_goals: int = 6,
) -> PredictionResult:
    adjusted_home_elo = home.elo + home_advantage_elo(match.neutral_site)
    elo_factor = elo_goal_factor(adjusted_home_elo, away.elo)

    home_momentum = 1.0 + _clamp(home.momentum, -0.15, 0.15)
    away_momentum = 1.0 + _clamp(away.momentum, -0.15, 0.15)

    home_lambda = (
        base_home_goals
        * home.attack_strength
        * away.defense_weakness
        * home_momentum
        * elo_factor
        / away.keeper_strength
    )
    away_lambda = (
        base_away_goals
        * away.attack_strength
        * home.defense_weakness
        * away_momentum
        / elo_factor
        / home.keeper_strength
    )

    home_lambda = _clamp(home_lambda, 0.15, 4.50)
    away_lambda = _clamp(away_lambda, 0.15, 4.50)

    home_win, draw, away_win = outcome_probabilities(home_lambda, away_lambda)
    matrix = score_matrix(home_lambda, away_lambda, max_goals=matrix_goals)

    return PredictionResult(
        match_id=match.match_id,
        date=match.date,
        home_team=match.home_team,
        away_team=match.away_team,
        home_lambda=home_lambda,
        away_lambda=away_lambda,
        home_win_prob=home_win,
        draw_prob=draw,
        away_win_prob=away_win,
        most_likely_score=most_likely_score(matrix),
        value_home=_value_index(home_win, match.home_odds),
        value_draw=_value_index(draw, match.draw_odds),
        value_away=_value_index(away_win, match.away_odds),
        score_matrix=matrix,
    )
