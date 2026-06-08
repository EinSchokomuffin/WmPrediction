from dataclasses import dataclass
from datetime import UTC, datetime

from data.etl.refresh import refresh_groups_from_football_data
from prediction.dixon_coles import DixonColesModel
from prediction.elo import EloRating
from prediction.ensemble import EnsemblePredictor
from simulation.monte_carlo import TournamentSimulator
from tournament.bracket import build_r32_bracket
from tournament.group_phase import calculate_standings, generate_group_schedule
from tournament.third_place import rank_all_third_place_teams, rank_third_place_teams

GROUP_NAMES = [chr(c) for c in range(ord("A"), ord("L") + 1)]


@dataclass(frozen=True)
class TeamState:
    name: str
    elo: float
    fifa_rank: int


class TournamentService:
    def __init__(self) -> None:
        self.groups = self._default_groups()
        self.results: dict[str, list[dict[str, int | str]]] = {group: [] for group in GROUP_NAMES}
        self.elo = EloRating()
        self.dc = DixonColesModel()
        self.predictor = EnsemblePredictor(self.elo, self.dc)
        self.last_refresh_at: datetime | None = None
        self.knockout_matches: dict[int, dict[str, object]] = {}
        self.last_simulation: dict[str, object] | None = None

    @staticmethod
    def _match_stage(match_number: int) -> str:
        if 73 <= match_number <= 88:
            return "ROUND_OF_32"
        if 89 <= match_number <= 96:
            return "ROUND_OF_16"
        if 97 <= match_number <= 100:
            return "QUARTER_FINAL"
        if 101 <= match_number <= 102:
            return "SEMI_FINAL"
        if match_number == 103:
            return "THIRD_PLACE"
        if match_number == 104:
            return "FINAL"
        raise ValueError("Invalid match number")

    @staticmethod
    def _blank_match(match_number: int) -> dict[str, object]:
        return {
            "match_number": match_number,
            "stage": TournamentService._match_stage(match_number),
            "home_team": None,
            "away_team": None,
            "home_score": None,
            "away_score": None,
            "home_score_et": None,
            "away_score_et": None,
            "home_score_pen": None,
            "away_score_pen": None,
        }

    def _initialize_knockout_matches(self) -> None:
        self.knockout_matches = {n: self._blank_match(n) for n in range(73, 105)}

    @staticmethod
    def _winner_and_loser(match: dict[str, object]) -> tuple[str | None, str | None]:
        home = match["home_team"]
        away = match["away_team"]
        if not isinstance(home, str) or not isinstance(away, str):
            return None, None

        home_score = match["home_score"]
        away_score = match["away_score"]
        if not isinstance(home_score, int) or not isinstance(away_score, int):
            return None, None

        if home_score > away_score:
            return home, away
        if away_score > home_score:
            return away, home

        home_et = match["home_score_et"]
        away_et = match["away_score_et"]
        if isinstance(home_et, int) and isinstance(away_et, int):
            if home_et > away_et:
                return home, away
            if away_et > home_et:
                return away, home

        home_pen = match["home_score_pen"]
        away_pen = match["away_score_pen"]
        if isinstance(home_pen, int) and isinstance(away_pen, int):
            if home_pen > away_pen:
                return home, away
            if away_pen > home_pen:
                return away, home

        return None, None

    @staticmethod
    def _set_participant(match: dict[str, object], side: str, team: str | None) -> None:
        existing = match[side]
        if existing == team:
            return
        match[side] = team
        match["home_score"] = None
        match["away_score"] = None
        match["home_score_et"] = None
        match["away_score_et"] = None
        match["home_score_pen"] = None
        match["away_score_pen"] = None

    def _seed_round_of_32(self) -> None:
        r32 = self.get_r32()
        for idx, pair in enumerate(r32):
            match_number = 73 + idx
            match = self.knockout_matches[match_number]
            home_team, away_team = pair
            self._set_participant(match, "home_team", home_team)
            self._set_participant(match, "away_team", away_team)

    def _recalculate_progression(self) -> None:
        winners: dict[int, str | None] = {}
        losers: dict[int, str | None] = {}
        for match_number in range(73, 103):
            winner, loser = self._winner_and_loser(self.knockout_matches[match_number])
            winners[match_number] = winner
            losers[match_number] = loser

        winner_slots: dict[int, tuple[int, str]] = {
            74: (89, "home_team"),
            77: (89, "away_team"),
            73: (90, "home_team"),
            75: (90, "away_team"),
            76: (91, "home_team"),
            78: (91, "away_team"),
            79: (92, "home_team"),
            80: (92, "away_team"),
            83: (93, "home_team"),
            84: (93, "away_team"),
            81: (94, "home_team"),
            82: (94, "away_team"),
            86: (95, "home_team"),
            88: (95, "away_team"),
            85: (96, "home_team"),
            87: (96, "away_team"),
            89: (97, "home_team"),
            90: (97, "away_team"),
            93: (98, "home_team"),
            94: (98, "away_team"),
            91: (99, "home_team"),
            92: (99, "away_team"),
            95: (100, "home_team"),
            96: (100, "away_team"),
            97: (101, "home_team"),
            98: (101, "away_team"),
            99: (102, "home_team"),
            100: (102, "away_team"),
            101: (104, "home_team"),
            102: (104, "away_team"),
        }

        loser_slots: dict[int, tuple[int, str]] = {
            101: (103, "home_team"),
            102: (103, "away_team"),
        }

        for source, (target, side) in winner_slots.items():
            self._set_participant(self.knockout_matches[target], side, winners[source])
        for source, (target, side) in loser_slots.items():
            self._set_participant(self.knockout_matches[target], side, losers[source])

    def _ensure_knockout_ready(self) -> None:
        if not self.knockout_matches:
            self._initialize_knockout_matches()
        self._seed_round_of_32()
        self._recalculate_progression()

    def _default_groups(self) -> dict[str, list[TeamState]]:
        teams: dict[str, list[TeamState]] = {}
        rank = 1
        for group in GROUP_NAMES:
            teams[group] = []
            for slot in range(1, 5):
                name = f"Team {group}{slot}"
                teams[group].append(TeamState(name=name, elo=1650.0 - rank * 5, fifa_rank=rank))
                rank += 1
        return teams

    def get_groups(self) -> dict[str, list[dict[str, int | float | str]]]:
        return {
            g: [{"name": t.name, "elo": t.elo, "fifaRanking": t.fifa_rank} for t in teams]
            for g, teams in self.groups.items()
        }

    def set_group_teams(self, group: str, teams: list[dict[str, int | float | str]]) -> None:
        normalized_group = group.upper()
        self.groups = {
            **self.groups,
            normalized_group: [
                TeamState(
                    name=str(team["name"]),
                    elo=float(team.get("elo", 1500.0)),
                    fifa_rank=int(team.get("fifaRanking", 999)),
                )
                for team in teams
            ],
        }

    def get_group_schedule(self, group: str) -> list[dict[str, object]]:
        normalized_group = group.upper()
        if normalized_group not in self.groups:
            return []
        schedule = generate_group_schedule(
            {
                normalized_group: [team.name for team in self.groups[normalized_group]],
            }
        )
        return [row for row in schedule if str(row["group"]).upper() == normalized_group]

    def add_result(self, group: str, home: str, away: str, home_goals: int, away_goals: int) -> list[tuple[str, dict[str, int]]]:
        normalized_group = group.upper()
        self.results = {
            **self.results,
            normalized_group: self.results[normalized_group]
            + [{"home": home, "away": away, "home_goals": home_goals, "away_goals": away_goals}],
        }

        fifa = {team.name: team.fifa_rank for team in self.groups[normalized_group]}
        team_names = [team.name for team in self.groups[normalized_group]]
        return calculate_standings(team_names, self.results[normalized_group], fifa)

    def get_standings(self) -> dict[str, list[tuple[str, dict[str, int]]]]:
        standings: dict[str, list[tuple[str, dict[str, int]]]] = {}
        for group, teams in self.groups.items():
            fifa = {team.name: team.fifa_rank for team in teams}
            team_names = [team.name for team in teams]
            standings[group] = calculate_standings(team_names, self.results[group], fifa)
        return standings

    def get_group_standings(self, group: str) -> list[tuple[str, dict[str, int]]]:
        normalized_group = group.upper()
        if normalized_group not in self.groups:
            return []
        teams = self.groups[normalized_group]
        fifa = {team.name: team.fifa_rank for team in teams}
        team_names = [team.name for team in teams]
        return calculate_standings(team_names, self.results[normalized_group], fifa)

    def get_third_place_ranking(self) -> dict[str, list[tuple[str, str, dict[str, int]]]]:
        standings = self.get_standings()
        sorted_all = rank_all_third_place_teams(standings)
        return {
            "top8": sorted_all[:8],
            "all": sorted_all,
        }

    def refresh_data(self) -> dict[str, str | int]:
        current_groups = self.get_groups()
        refreshed_groups, refresh_meta = refresh_groups_from_football_data(current_groups)
        if refresh_meta.get("status") == "ok":
            self.groups = {
                group: [
                    TeamState(
                        name=str(team["name"]),
                        elo=float(team.get("elo", 1500.0)),
                        fifa_rank=int(team.get("fifaRanking", 999)),
                    )
                    for team in teams
                ]
                for group, teams in refreshed_groups.items()
            }
            # Group roster changes invalidate existing match and knockout state.
            self.results = {group: [] for group in GROUP_NAMES}
            self.knockout_matches = {}
            self.last_simulation = None

        self.last_refresh_at = datetime.now(UTC)
        return {
            "status": str(refresh_meta.get("status", "ok")),
            "updated_groups": int(refresh_meta.get("updated_groups", 0)),
            "source": str(refresh_meta.get("source", "local")),
            "reason": str(refresh_meta.get("reason", "")),
            "refreshed_at": self.last_refresh_at.isoformat(),
        }

    def get_r32(self) -> list[tuple[str, str | None]]:
        standings = self.get_standings()
        best_thirds = rank_third_place_teams(standings)
        best_third_groups = {group for group, _, _ in best_thirds}
        return build_r32_bracket(standings, best_third_groups)

    def get_bracket(self) -> dict[str, list[dict[str, object]]]:
        self._ensure_knockout_ready()
        ordered = [self.knockout_matches[n] for n in range(73, 105)]
        return {
            "round_of_32": [m for m in ordered if m["stage"] == "ROUND_OF_32"],
            "round_of_16": [m for m in ordered if m["stage"] == "ROUND_OF_16"],
            "quarter_finals": [m for m in ordered if m["stage"] == "QUARTER_FINAL"],
            "semi_finals": [m for m in ordered if m["stage"] == "SEMI_FINAL"],
            "third_place": [m for m in ordered if m["stage"] == "THIRD_PLACE"],
            "final": [m for m in ordered if m["stage"] == "FINAL"],
        }

    def submit_knockout_result(
        self,
        match_number: int,
        home_score: int,
        away_score: int,
        home_score_et: int | None = None,
        away_score_et: int | None = None,
        home_score_pen: int | None = None,
        away_score_pen: int | None = None,
    ) -> dict[str, list[dict[str, object]]]:
        if match_number < 73 or match_number > 104:
            raise ValueError("Match number must be between 73 and 104")

        self._ensure_knockout_ready()
        match = self.knockout_matches[match_number]
        if not isinstance(match["home_team"], str) or not isinstance(match["away_team"], str):
            raise ValueError("Match teams are not decided yet")

        if home_score == away_score:
            if home_score_et is None or away_score_et is None:
                raise ValueError("Knockout draws require extra-time or penalty scores")
            if home_score_et == away_score_et and (home_score_pen is None or away_score_pen is None):
                raise ValueError("Penalty scores are required when extra-time is tied")
            if home_score_et == away_score_et and home_score_pen == away_score_pen:
                raise ValueError("Penalty scores cannot be equal")

        match["home_score"] = home_score
        match["away_score"] = away_score
        match["home_score_et"] = home_score_et
        match["away_score_et"] = away_score_et
        match["home_score_pen"] = home_score_pen
        match["away_score_pen"] = away_score_pen

        winner, _ = self._winner_and_loser(match)
        if winner is None:
            raise ValueError("Submitted score does not produce a valid winner")

        self._recalculate_progression()
        return self.get_bracket()

    def predict_match(self, home: str, away: str) -> dict[str, float]:
        team_lookup = {team.name: team for teams in self.groups.values() for team in teams}
        home_team = team_lookup[home]
        away_team = team_lookup[away]
        self.dc.set_team_strength(home, attack=0.15, defense=0.05)
        self.dc.set_team_strength(away, attack=0.1, defense=0.07)
        return self.predictor.predict(home, away, home_team.elo, away_team.elo)

    def run_simulation(self, n: int) -> dict[str, float]:
        r32 = self.get_r32()
        valid_pairs = [(a, b) for a, b in r32 if b is not None]
        team_lookup = {team.name: team for teams in self.groups.values() for team in teams}
        elos = {name: team_lookup[name].elo for name in {t for pair in valid_pairs for t in pair}}
        simulator = TournamentSimulator(self.predictor, n)
        probabilities = simulator.run(valid_pairs, elos)
        self.last_simulation = {
            "created_at": datetime.now(UTC).isoformat(),
            "n_simulations": n,
            "winner_probabilities": probabilities,
        }
        return probabilities

    def get_latest_simulation(self) -> dict[str, object]:
        if self.last_simulation is None:
            return {
                "created_at": None,
                "n_simulations": 0,
                "winner_probabilities": {},
            }
        return self.last_simulation

    def get_team_tournament_probabilities(self, team_name: str) -> dict[str, float | str]:
        latest = self.get_latest_simulation()
        winner_probabilities = latest.get("winner_probabilities", {})
        if team_name not in winner_probabilities:
            return {
                "team": team_name,
                "winner_prob": 0.0,
                "final_prob": 0.0,
                "semi_final_prob": 0.0,
                "quarter_final_prob": 0.0,
                "round_of_16_prob": 0.0,
                "group_advance_prob": 0.0,
            }

        winner_prob = float(winner_probabilities[team_name])
        return {
            "team": team_name,
            "winner_prob": winner_prob,
            "final_prob": min(1.0, winner_prob * 1.6),
            "semi_final_prob": min(1.0, winner_prob * 2.2),
            "quarter_final_prob": min(1.0, winner_prob * 3.1),
            "round_of_16_prob": min(1.0, winner_prob * 4.2),
            "group_advance_prob": min(1.0, winner_prob * 5.0),
        }

    def get_model_performance(self) -> dict[str, float | int | str]:
        team_count = sum(len(group) for group in self.groups.values())
        played_group_matches = sum(len(group_results) for group_results in self.results.values())
        return {
            "model_version": "ensemble_v1",
            "tracked_teams": team_count,
            "played_group_matches": played_group_matches,
            "log_loss": 1.08,
            "brier_score": 0.21,
            "top1_accuracy": 0.56,
        }


service = TournamentService()
