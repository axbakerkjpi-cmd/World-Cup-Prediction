import math
from typing import Dict, Tuple


def poisson_pmf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def score_matrix(home_lambda: float, away_lambda: float, max_goals: int = 6) -> Dict[str, float]:
    matrix: Dict[str, float] = {}
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            key = f"{home_goals}-{away_goals}"
            matrix[key] = poisson_pmf(home_goals, home_lambda) * poisson_pmf(away_goals, away_lambda)
    return matrix


def outcome_probabilities(home_lambda: float, away_lambda: float, max_goals: int = 12) -> Tuple[float, float, float]:
    home_win = 0.0
    draw = 0.0
    away_win = 0.0

    for home_goals in range(max_goals + 1):
        home_prob = poisson_pmf(home_goals, home_lambda)
        for away_goals in range(max_goals + 1):
            prob = home_prob * poisson_pmf(away_goals, away_lambda)
            if home_goals > away_goals:
                home_win += prob
            elif home_goals == away_goals:
                draw += prob
            else:
                away_win += prob

    covered = home_win + draw + away_win
    if covered <= 0:
        return 0.0, 0.0, 0.0
    return home_win / covered, draw / covered, away_win / covered


def most_likely_score(matrix: Dict[str, float]) -> str:
    return max(matrix.items(), key=lambda item: item[1])[0]
