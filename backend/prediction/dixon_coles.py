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

    @staticmethod
    def _project_scoreline(expected_home: float, expected_away: float, home_win: float, draw: float, away_win: float) -> tuple[int, int]:
        if draw >= home_win and draw >= away_win:
            goals = max(0, round((expected_home + expected_away) / 2))
            return goals, goals

        if home_win >= away_win:
            projected_home = max(1, math.ceil(expected_home + 0.35))
            projected_away = max(0, math.floor(expected_away + 0.15))
            if projected_home <= projected_away:
                projected_home = projected_away + 1
            return projected_home, projected_away

        projected_away = max(1, math.ceil(expected_away + 0.35))
        projected_home = max(0, math.floor(expected_home + 0.15))
        if projected_away <= projected_home:
            projected_away = projected_home + 1
        return projected_home, projected_away

    def predict_match(self, home: str, away: str, max_goals: int = 8) -> dict[str, float]:
        mu_home, mu_away = self._mu(home, away)
        matrix = np.outer(
            poisson.pmf(np.arange(max_goals + 1), mu_home),
            poisson.pmf(np.arange(max_goals + 1), mu_away),
        )
        matrix = matrix / matrix.sum()
        home_win = float(np.tril(matrix, -1).sum())
        draw = float(np.trace(matrix))
        away_win = float(np.triu(matrix, 1).sum())
        goals = np.arange(max_goals + 1)
        expected_home = float(np.dot(matrix.sum(axis=1), goals))
        expected_away = float(np.dot(matrix.sum(axis=0), goals))
        projected_home, projected_away = self._project_scoreline(expected_home, expected_away, home_win, draw, away_win)
        return {
            "home_win_prob": home_win,
            "draw_prob": draw,
            "away_win_prob": away_win,
            "expected_home_goals": expected_home,
            "expected_away_goals": expected_away,
            "most_likely_home_goals": projected_home,
            "most_likely_away_goals": projected_away,
        }
