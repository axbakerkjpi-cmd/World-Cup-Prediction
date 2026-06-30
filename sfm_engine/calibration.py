import math
from typing import Iterable, Sequence


def brier_score(probabilities: Sequence[float], actual_index: int) -> float:
    return sum((prob - (1.0 if idx == actual_index else 0.0)) ** 2 for idx, prob in enumerate(probabilities))


def mean_brier_score(rows: Iterable[Sequence[float]], actual_indices: Iterable[int]) -> float:
    scores = [brier_score(probabilities, actual) for probabilities, actual in zip(rows, actual_indices)]
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def log_loss(probabilities: Sequence[float], actual_index: int, epsilon: float = 1e-12) -> float:
    probability = min(1.0 - epsilon, max(epsilon, probabilities[actual_index]))
    return -math.log(probability)
