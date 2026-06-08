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

    @staticmethod
    def _attack_strength(elo: float, rank: int, home_advantage: bool = False) -> float:
        elo_factor = (elo - 1500.0) / 180.0
        rank_factor = (50.0 - rank) / 50.0
        base = 0.12 + elo_factor * 0.18 + rank_factor * 0.12
        if home_advantage:
            base += 0.08
        return max(-0.35, min(0.45, base))

    @staticmethod
    def _defense_strength(elo: float, rank: int) -> float:
        elo_factor = (elo - 1500.0) / 200.0
        rank_factor = (50.0 - rank) / 60.0
        return max(-0.25, min(0.35, 0.08 + elo_factor * 0.14 + rank_factor * 0.08))

    def predict(
        self,
        home: str,
        away: str,
        home_elo: float,
        away_elo: float,
        home_rank: int,
        away_rank: int,
    ) -> dict[str, float]:
        self.dc.set_team_strength(
            home,
            attack=self._attack_strength(home_elo, home_rank, home_advantage=True),
            defense=self._defense_strength(home_elo, home_rank),
        )
        self.dc.set_team_strength(
            away,
            attack=self._attack_strength(away_elo, away_rank, home_advantage=False),
            defense=self._defense_strength(away_elo, away_rank),
        )

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
