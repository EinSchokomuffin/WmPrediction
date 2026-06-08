from prediction.dixon_coles import DixonColesModel
from prediction.elo import EloRating
from prediction.ml_workflow import TrainedMatchModel


class EnsemblePredictor:
    def __init__(self, elo: EloRating, dc: DixonColesModel, ml_model: TrainedMatchModel | None = None) -> None:
        self.elo = elo
        self.dc = dc
        self.ml_model = ml_model

    def set_ml_model(self, ml_model: TrainedMatchModel | None) -> None:
        self.ml_model = ml_model

    def predict(
        self,
        home: str,
        away: str,
        home_elo: float,
        away_elo: float,
        home_rank: int,
        away_rank: int,
    ) -> dict[str, float]:
        elo_pred = self.elo.win_probability(home_elo, away_elo)
        dc_pred = self.dc.predict_match(home, away)
        ml_pred = (
            self.ml_model.predict(home, away, home_elo, away_elo, home_rank, away_rank)
            if self.ml_model is not None
            else None
        )

        if ml_pred is None:
            home_win = 0.35 * elo_pred["home_win"] + 0.65 * dc_pred["home_win_prob"]
            draw = 0.35 * elo_pred["draw"] + 0.65 * dc_pred["draw_prob"]
        else:
            home_win = (
                0.25 * elo_pred["home_win"]
                + 0.45 * dc_pred["home_win_prob"]
                + 0.30 * ml_pred["home_win_prob"]
            )
            draw = (
                0.25 * elo_pred["draw"]
                + 0.45 * dc_pred["draw_prob"]
                + 0.30 * ml_pred["draw_prob"]
            )

        away_win = max(0.0, 1.0 - home_win - draw)
        return {
            "home_win_prob": home_win,
            "draw_prob": draw,
            "away_win_prob": away_win,
            "expected_home_goals": dc_pred["expected_home_goals"],
            "expected_away_goals": dc_pred["expected_away_goals"],
            "confidence": max(home_win, draw, away_win),
        }
