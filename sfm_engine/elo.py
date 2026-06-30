import math


def elo_goal_factor(elo_a: float, elo_b: float, scale: float = 900.0) -> float:
    """Convert an Elo gap into a moderate multiplier for expected goals."""
    factor = math.exp((elo_a - elo_b) / scale)
    return min(1.45, max(0.69, factor))


def home_advantage_elo(neutral_site: bool, advantage: float = 55.0) -> float:
    return 0.0 if neutral_site else advantage
