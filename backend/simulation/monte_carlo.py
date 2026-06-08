from collections import defaultdict

import numpy as np


class TournamentSimulator:
    def __init__(self, predictor, n_simulations: int = 1000):
        self.predictor = predictor
        self.n_simulations = n_simulations

    def simulate_match(
        self,
        home: str,
        away: str,
        home_elo: float,
        away_elo: float,
        home_rank: int = 100,
        away_rank: int = 100,
    ) -> str:
        pred = self.predictor.predict(home, away, home_elo, away_elo, home_rank, away_rank)
        probs = [pred["home_win_prob"], pred["draw_prob"], pred["away_win_prob"]]
        outcome = np.random.choice(["H", "D", "A"], p=probs)
        if outcome == "H":
            return home
        if outcome == "A":
            return away
        return np.random.choice([home, away]).item()

    def run_knockout(self, pairs: list[tuple[str, str]], elos: dict[str, float], ranks: dict[str, int]) -> str:
        round_teams = list(pairs)
        while len(round_teams) > 1:
            winners = []
            for home, away in round_teams:
                winners.append(self.simulate_match(home, away, elos[home], elos[away], ranks[home], ranks[away]))
            round_teams = [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]
        return self.simulate_match(
            round_teams[0][0],
            round_teams[0][1],
            elos[round_teams[0][0]],
            elos[round_teams[0][1]],
            ranks[round_teams[0][0]],
            ranks[round_teams[0][1]],
        )

    def run(self, pairs: list[tuple[str, str]], elos: dict[str, float], ranks: dict[str, int]) -> dict[str, float]:
        counts = defaultdict(int)
        for _ in range(self.n_simulations):
            winner = self.run_knockout(pairs, elos, ranks)
            counts[winner] += 1
        return {team: count / self.n_simulations for team, count in counts.items()}
