import random
from typing import Dict

from .poisson import poisson_pmf


def _sample_poisson(lam: float, rng: random.Random) -> int:
    threshold = rng.random()
    cumulative = 0.0
    goals = 0
    while goals < 12:
        cumulative += poisson_pmf(goals, lam)
        if threshold <= cumulative:
            return goals
        goals += 1
    return goals


def simulate_match(home_lambda: float, away_lambda: float, trials: int = 10000, seed: int = 7) -> Dict[str, float]:
    rng = random.Random(seed)
    home_wins = 0
    draws = 0
    away_wins = 0

    for _ in range(trials):
        home_goals = _sample_poisson(home_lambda, rng)
        away_goals = _sample_poisson(away_lambda, rng)
        if home_goals > away_goals:
            home_wins += 1
        elif home_goals == away_goals:
            draws += 1
        else:
            away_wins += 1

    return {
        "home_win": home_wins / trials,
        "draw": draws / trials,
        "away_win": away_wins / trials,
    }
