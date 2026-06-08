from prediction.dixon_coles import DixonColesModel
from prediction.elo import EloRating


class EnsemblePredictor:
    def __init__(self, elo: EloRating, dc: DixonColesModel) -> None:
        self.elo = elo
        self.dc = dc

    def predict(self, home: str, away: str, home_elo: float, away_elo: float) -> dict[str, float]:
        elo_pred = self.elo.win_probability(home_elo, away_elo)
        dc_pred = self.dc.predict_match(home, away)
        home_win = 0.35 * elo_pred["home_win"] + 0.65 * dc_pred["home_win_prob"]
        draw = 0.35 * elo_pred["draw"] + 0.65 * dc_pred["draw_prob"]
        away_win = max(0.0, 1.0 - home_win - draw)
        return {
            "home_win_prob": home_win,
            "draw_prob": draw,
            "away_win_prob": away_win,
            "expected_home_goals": dc_pred["expected_home_goals"],
            "expected_away_goals": dc_pred["expected_away_goals"],
            "confidence": max(home_win, draw, away_win),
        }
