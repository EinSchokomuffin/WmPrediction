import math

import numpy as np
from scipy.stats import poisson


class DixonColesModel:
    def __init__(self) -> None:
        self.attack: dict[str, float] = {}
        self.defense: dict[str, float] = {}

    def set_team_strength(self, team: str, attack: float, defense: float) -> None:
        self.attack[team] = attack
        self.defense[team] = defense

    def _mu(self, home: str, away: str) -> tuple[float, float]:
        a_h = self.attack.get(home, 0.0)
        d_h = self.defense.get(home, 0.0)
        a_a = self.attack.get(away, 0.0)
        d_a = self.defense.get(away, 0.0)
        mu_home = math.exp(a_h - d_a)
        mu_away = math.exp(a_a - d_h)
        return mu_home, mu_away

    def predict_match(self, home: str, away: str, max_goals: int = 8) -> dict[str, float]:
        mu_home, mu_away = self._mu(home, away)
        matrix = np.outer(
            poisson.pmf(np.arange(max_goals + 1), mu_home),
            poisson.pmf(np.arange(max_goals + 1), mu_away),
        )
        matrix = matrix / matrix.sum()
        most_likely_index = np.unravel_index(np.argmax(matrix), matrix.shape)
        home_win = float(np.tril(matrix, -1).sum())
        draw = float(np.trace(matrix))
        away_win = float(np.triu(matrix, 1).sum())
        goals = np.arange(max_goals + 1)
        expected_home = float(np.dot(matrix.sum(axis=1), goals))
        expected_away = float(np.dot(matrix.sum(axis=0), goals))
        return {
            "home_win_prob": home_win,
            "draw_prob": draw,
            "away_win_prob": away_win,
            "expected_home_goals": expected_home,
            "expected_away_goals": expected_away,
            "most_likely_home_goals": int(most_likely_index[0]),
            "most_likely_away_goals": int(most_likely_index[1]),
        }
