class EloRating:
    BASE_RATING = 1500.0

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

    def win_probability(self, elo_a: float, elo_b: float) -> dict[str, float]:
        win = self.expected_score(elo_a, elo_b)
        draw = 0.25 * (1.0 - abs(win - 0.5) * 2.0)
        home = win * (1.0 - draw)
        away = (1.0 - win) * (1.0 - draw)
        total = home + draw + away
        return {"home_win": home / total, "draw": draw / total, "away_win": away / total}
