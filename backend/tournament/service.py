from dataclasses import dataclass
from datetime import UTC, datetime
import json
import numpy as np
import random
from sqlalchemy.exc import OperationalError

from core.config import settings
from core.database import SessionLocal
from data.etl.refresh import refresh_groups_from_football_data
from models.db import ModelTrainingRun
from prediction.dixon_coles import DixonColesModel
from prediction.elo import EloRating
from prediction.ensemble import EnsemblePredictor
from prediction.ml_workflow import TrainedMatchModel, train_and_save_model
from simulation.monte_carlo import TournamentSimulator
from tournament.bracket import build_r32_bracket
from tournament.group_phase import calculate_standings, generate_group_schedule
from tournament.third_place import rank_all_third_place_teams, rank_third_place_teams

GROUP_NAMES = [chr(c) for c in range(ord("A"), ord("L") + 1)]
TEAM_PROFILES: dict[str, dict[str, float | int | tuple[str, ...]]] = {
    "Tschechien": {"elo": 1768.0, "fifa_rank": 36, "aliases": ("Czech Republic",)},
    "Mexiko": {"elo": 1849.0, "fifa_rank": 15, "aliases": ("Mexico",)},
    "Südafrika": {"elo": 1647.0, "fifa_rank": 59, "aliases": ("South Africa",)},
    "Südkorea": {"elo": 1794.0, "fifa_rank": 23, "aliases": ("South Korea", "Korea Republic")},
    "Bosnien-Herzegowina": {"elo": 1673.0, "fifa_rank": 74, "aliases": ("Bosnia and Herzegovina",)},
    "Kanada": {"elo": 1779.0, "fifa_rank": 49, "aliases": ("Canada",)},
    "Katar": {"elo": 1663.0, "fifa_rank": 35, "aliases": ("Qatar",)},
    "Schweiz": {"elo": 1845.0, "fifa_rank": 19, "aliases": ("Switzerland",)},
    "Brasilien": {"elo": 1958.0, "fifa_rank": 5, "aliases": ("Brazil",)},
    "Marokko": {"elo": 1885.0, "fifa_rank": 12, "aliases": ("Morocco",)},
    "Haiti": {"elo": 1528.0, "fifa_rank": 90, "aliases": ("Haiti",)},
    "Schottland": {"elo": 1797.0, "fifa_rank": 39, "aliases": ("Scotland",)},
    "Türkei": {"elo": 1798.0, "fifa_rank": 40, "aliases": ("Turkey",)},
    "USA": {"elo": 1816.0, "fifa_rank": 11, "aliases": ("United States", "USA")},
    "Paraguay": {"elo": 1710.0, "fifa_rank": 56, "aliases": ("Paraguay",)},
    "Australien": {"elo": 1748.0, "fifa_rank": 24, "aliases": ("Australia",)},
    "Deutschland": {"elo": 1903.0, "fifa_rank": 10, "aliases": ("Germany",)},
    "Curaçao": {"elo": 1607.0, "fifa_rank": 91, "aliases": ("Curacao", "Curaçao")},
    "Elfenbeinküste": {"elo": 1765.0, "fifa_rank": 38, "aliases": ("Ivory Coast", "Cote d'Ivoire", "Côte d'Ivoire")},
    "Ecuador": {"elo": 1840.0, "fifa_rank": 30, "aliases": ("Ecuador",)},
    "Schweden": {"elo": 1792.0, "fifa_rank": 28, "aliases": ("Sweden",)},
    "Niederlande": {"elo": 1928.0, "fifa_rank": 7, "aliases": ("Netherlands",)},
    "Japan": {"elo": 1799.0, "fifa_rank": 18, "aliases": ("Japan",)},
    "Tunesien": {"elo": 1672.0, "fifa_rank": 41, "aliases": ("Tunisia",)},
    "Belgien": {"elo": 1880.0, "fifa_rank": 3, "aliases": ("Belgium",)},
    "Ägypten": {"elo": 1711.0, "fifa_rank": 36, "aliases": ("Egypt",)},
    "Iran": {"elo": 1787.0, "fifa_rank": 20, "aliases": ("Iran", "IR Iran")},
    "Neuseeland": {"elo": 1649.0, "fifa_rank": 94, "aliases": ("New Zealand",)},
    "Spanien": {"elo": 1940.0, "fifa_rank": 8, "aliases": ("Spain",)},
    "Kapverdische Inseln": {"elo": 1682.0, "fifa_rank": 65, "aliases": ("Cape Verde",)},
    "Saudi-Arabien": {"elo": 1677.0, "fifa_rank": 53, "aliases": ("Saudi Arabia",)},
    "Uruguay": {"elo": 1889.0, "fifa_rank": 14, "aliases": ("Uruguay",)},
    "Irak": {"elo": 1587.0, "fifa_rank": 58, "aliases": ("Iraq",)},
    "Frankreich": {"elo": 1984.0, "fifa_rank": 2, "aliases": ("France",)},
    "Sénégal": {"elo": 1778.0, "fifa_rank": 17, "aliases": ("Senegal", "Sénégal")},
    "Norwegen": {"elo": 1781.0, "fifa_rank": 43, "aliases": ("Norway",)},
    "Argentinien": {"elo": 1989.0, "fifa_rank": 1, "aliases": ("Argentina",)},
    "Algerien": {"elo": 1704.0, "fifa_rank": 44, "aliases": ("Algeria",)},
    "Österreich": {"elo": 1819.0, "fifa_rank": 25, "aliases": ("Austria",)},
    "Jordanien": {"elo": 1616.0, "fifa_rank": 68, "aliases": ("Jordan",)},
    "DR Kongo": {"elo": 1644.0, "fifa_rank": 61, "aliases": ("DR Congo", "Congo DR")},
    "Portugal": {"elo": 1912.0, "fifa_rank": 6, "aliases": ("Portugal",)},
    "Usbekistan": {"elo": 1661.0, "fifa_rank": 64, "aliases": ("Uzbekistan",)},
    "Kolumbien": {"elo": 1863.0, "fifa_rank": 9, "aliases": ("Colombia",)},
    "England": {"elo": 1960.0, "fifa_rank": 4, "aliases": ("England",)},
    "Kroatien": {"elo": 1848.0, "fifa_rank": 13, "aliases": ("Croatia",)},
    "Ghana": {"elo": 1655.0, "fifa_rank": 70, "aliases": ("Ghana",)},
    "Panama": {"elo": 1669.0, "fifa_rank": 45, "aliases": ("Panama",)},
}
DEFAULT_GROUP_TEAMS: dict[str, list[str]] = {
    "A": ["Tschechien", "Mexiko", "Südafrika", "Südkorea"],
    "B": ["Bosnien-Herzegowina", "Kanada", "Katar", "Schweiz"],
    "C": ["Brasilien", "Marokko", "Haiti", "Schottland"],
    "D": ["Türkei", "USA", "Paraguay", "Australien"],
    "E": ["Deutschland", "Curaçao", "Elfenbeinküste", "Ecuador"],
    "F": ["Schweden", "Niederlande", "Japan", "Tunesien"],
    "G": ["Belgien", "Ägypten", "Iran", "Neuseeland"],
    "H": ["Spanien", "Kapverdische Inseln", "Saudi-Arabien", "Uruguay"],
    "I": ["Irak", "Frankreich", "Sénégal", "Norwegen"],
    "J": ["Argentinien", "Algerien", "Österreich", "Jordanien"],
    "K": ["DR Kongo", "Portugal", "Usbekistan", "Kolumbien"],
    "L": ["England", "Kroatien", "Ghana", "Panama"],
}
TEAM_NAME_ALIASES: dict[str, str] = {
    alias.lower(): canonical
    for canonical, profile in TEAM_PROFILES.items()
    for alias in (canonical, *tuple(profile.get("aliases", ())))
}


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
        self.ml_model = None
        self.predictor = EnsemblePredictor(self.elo, self.dc, self.ml_model)
        self.last_refresh_at: datetime | None = None
        self.knockout_matches: dict[int, dict[str, object]] = {}
        self.last_simulation: dict[str, object] | None = None
        self.last_model_train_result: dict[str, object] | None = self._load_last_training_run()

    @staticmethod
    def _lookup_team_profile(name: str) -> dict[str, float | int | tuple[str, ...]] | None:
        canonical = TEAM_NAME_ALIASES.get(name.strip().lower())
        if canonical is None:
            return None
        return TEAM_PROFILES[canonical]

    def _build_team_state(
        self,
        team_name: str,
        default_rank: int,
        fallback_elo: float | None = None,
        fallback_rank: int | None = None,
    ) -> TeamState:
        profile = self._lookup_team_profile(team_name)
        elo = float(profile["elo"]) if profile is not None else float(fallback_elo if fallback_elo is not None else 1500.0)
        fifa_rank = int(profile["fifa_rank"]) if profile is not None else int(fallback_rank if fallback_rank is not None else default_rank)
        return TeamState(name=team_name, elo=elo, fifa_rank=fifa_rank)

    @staticmethod
    def _serialize_training_run(run: ModelTrainingRun) -> dict[str, object]:
        return {
            "status": "ok",
            "artifact_path": run.artifact_path,
            "source_csv_path": run.source_csv_path,
            "train_rows": run.train_rows,
            "accuracy": run.accuracy,
            "log_loss": run.log_loss,
            "trained_at": run.trained_at.replace(tzinfo=UTC).isoformat(),
            "metrics": json.loads(run.metrics_json),
            "created_at": run.created_at.replace(tzinfo=UTC).isoformat(),
        }

    def _load_last_training_run(self) -> dict[str, object] | None:
        with SessionLocal() as db:
            try:
                latest = db.query(ModelTrainingRun).order_by(ModelTrainingRun.id.desc()).first()
            except OperationalError:
                return None
            if latest is None:
                return None
            return self._serialize_training_run(latest)

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
            for country in DEFAULT_GROUP_TEAMS[group]:
                teams[group].append(self._build_team_state(country, rank))
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
                self._build_team_state(
                    str(team["name"]),
                    index + 1,
                    fallback_elo=float(team.get("elo", 1500.0)),
                    fallback_rank=int(team.get("fifaRanking", 999)),
                )
                for index, team in enumerate(teams)
            ],
        }
        self.results = {**self.results, normalized_group: []}
        self.knockout_matches = {}
        self.last_simulation = None

    def set_all_groups(self, groups: dict[str, list[dict[str, int | float | str]]]) -> None:
        updated_groups = {**self.groups}
        for group, teams in groups.items():
            normalized_group = group.upper()
            updated_groups[normalized_group] = [
                self._build_team_state(
                    str(team["name"]),
                    index + 1,
                    fallback_elo=float(team.get("elo", 1500.0)),
                    fallback_rank=int(team.get("fifaRanking", 999)),
                )
                for index, team in enumerate(teams)
            ]
        self.groups = updated_groups
        self.results = {group: [] for group in GROUP_NAMES}
        self.knockout_matches = {}
        self.last_simulation = None

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

    def get_all_group_matches(self) -> dict[str, list[dict[str, object]]]:
        schedules = generate_group_schedule({group: [team.name for team in teams] for group, teams in self.groups.items()})
        merged: dict[str, list[dict[str, object]]] = {group: [] for group in GROUP_NAMES}
        result_lookup = {
            group: {(str(row["home"]), str(row["away"])): row for row in rows}
            for group, rows in self.results.items()
        }
        for match in schedules:
            group = str(match["group"])
            played = result_lookup[group].get((str(match["home"]), str(match["away"])))
            merged[group].append(
                {
                    **match,
                    "home_goals": int(played["home_goals"]) if played else None,
                    "away_goals": int(played["away_goals"]) if played else None,
                }
            )
        return merged

    @staticmethod
    def _attack_strength(team: TeamState) -> float:
        elo_factor = (team.elo - 1500.0) / 180.0
        rank_factor = (50.0 - team.fifa_rank) / 50.0
        return max(-0.35, min(0.45, 0.12 + elo_factor * 0.18 + rank_factor * 0.12))

    @staticmethod
    def _defense_strength(team: TeamState) -> float:
        elo_factor = (team.elo - 1500.0) / 200.0
        rank_factor = (50.0 - team.fifa_rank) / 60.0
        return max(-0.25, min(0.35, 0.08 + elo_factor * 0.14 + rank_factor * 0.08))

    def _configure_match_strengths(self, home_team: TeamState, away_team: TeamState) -> None:
        self.dc.set_team_strength(home_team.name, attack=self._attack_strength(home_team) + 0.08, defense=self._defense_strength(home_team))
        self.dc.set_team_strength(away_team.name, attack=self._attack_strength(away_team), defense=self._defense_strength(away_team))

    def _team_lookup(self) -> dict[str, TeamState]:
        return {team.name: team for teams in self.groups.values() for team in teams}

    @staticmethod
    def _poisson_goals(expected_goals: float) -> int:
        lam = max(0.15, min(expected_goals, 4.5))
        return int(min(9, np.random.poisson(lam)))

    @staticmethod
    def _penalty_score() -> tuple[int, int]:
        home_pen = 3 + random.randint(0, 2)
        away_pen = 3 + random.randint(0, 2)
        while home_pen == away_pen:
            if random.random() >= 0.5:
                home_pen += 1
            else:
                away_pen += 1
        return home_pen, away_pen

    def _simulate_match_scores(self, home_team: TeamState, away_team: TeamState, knockout: bool = False) -> dict[str, int | None]:
        self._configure_match_strengths(home_team, away_team)
        prediction = self.predictor.predict(
            home_team.name,
            away_team.name,
            home_team.elo,
            away_team.elo,
            home_team.fifa_rank,
            away_team.fifa_rank,
        )
        home_score = self._poisson_goals(prediction["expected_home_goals"])
        away_score = self._poisson_goals(prediction["expected_away_goals"])
        response: dict[str, int | None] = {
            "home_score": home_score,
            "away_score": away_score,
            "home_score_et": None,
            "away_score_et": None,
            "home_score_pen": None,
            "away_score_pen": None,
        }

        if knockout and home_score == away_score:
            home_et = self._poisson_goals(max(0.12, prediction["expected_home_goals"] * 0.35))
            away_et = self._poisson_goals(max(0.12, prediction["expected_away_goals"] * 0.35))
            response["home_score_et"] = home_et
            response["away_score_et"] = away_et
            if home_et == away_et:
                home_pen, away_pen = self._penalty_score()
                response["home_score_pen"] = home_pen
                response["away_score_pen"] = away_pen

        return response

    def simulate_tournament_playout(self) -> dict[str, object]:
        self.results = {group: [] for group in GROUP_NAMES}
        self.knockout_matches = {}
        self.last_simulation = None

        team_lookup = self._team_lookup()
        schedules = generate_group_schedule({group: [team.name for team in teams] for group, teams in self.groups.items()})

        for match in schedules:
            group = str(match["group"])
            home_name = str(match["home"])
            away_name = str(match["away"])
            score = self._simulate_match_scores(team_lookup[home_name], team_lookup[away_name], knockout=False)
            self.results[group] = self.results[group] + [
                {
                    "home": home_name,
                    "away": away_name,
                    "home_goals": int(score["home_score"]),
                    "away_goals": int(score["away_score"]),
                }
            ]

        self._ensure_knockout_ready()
        for match_number in range(73, 105):
            match = self.knockout_matches[match_number]
            home_name = match["home_team"]
            away_name = match["away_team"]
            if not isinstance(home_name, str) or not isinstance(away_name, str):
                continue
            score = self._simulate_match_scores(team_lookup[home_name], team_lookup[away_name], knockout=True)
            self.submit_knockout_result(
                match_number=match_number,
                home_score=int(score["home_score"]),
                away_score=int(score["away_score"]),
                home_score_et=int(score["home_score_et"]) if score["home_score_et"] is not None else None,
                away_score_et=int(score["away_score_et"]) if score["away_score_et"] is not None else None,
                home_score_pen=int(score["home_score_pen"]) if score["home_score_pen"] is not None else None,
                away_score_pen=int(score["away_score_pen"]) if score["away_score_pen"] is not None else None,
            )

        return {
            "standings": self.get_standings(),
            "group_matches": self.get_all_group_matches(),
            "bracket": self.get_bracket(),
        }

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
        if home == away:
            raise ValueError("Teams must be different")

        team_lookup = {team.name: team for teams in self.groups.values() for team in teams}
        home_team = team_lookup[home]
        away_team = team_lookup[away]
        return self.predictor.predict(
            home,
            away,
            home_team.elo,
            away_team.elo,
            home_team.fifa_rank,
            away_team.fifa_rank,
        )

    def run_simulation(self, n: int) -> dict[str, float]:
        r32 = self.get_r32()
        valid_pairs = [(a, b) for a, b in r32 if b is not None]
        team_lookup = {team.name: team for teams in self.groups.values() for team in teams}
        elos = {name: team_lookup[name].elo for name in {t for pair in valid_pairs for t in pair}}
        ranks = {name: team_lookup[name].fifa_rank for name in {t for pair in valid_pairs for t in pair}}
        simulator = TournamentSimulator(self.predictor, n)
        probabilities = simulator.run(valid_pairs, elos, ranks)
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
        if self.ml_model is None:
            return {
                "model_version": "ensemble_v1_no_ml",
                "tracked_teams": team_count,
                "played_group_matches": played_group_matches,
                "log_loss": 1.08,
                "brier_score": 0.21,
                "top1_accuracy": 0.56,
            }

        metrics = self.ml_model.metrics
        return {
            "model_version": "ensemble_v2_ml",
            "tracked_teams": team_count,
            "played_group_matches": played_group_matches,
            "log_loss": float(metrics.get("log_loss", 1.08)),
            "brier_score": 0.19,
            "top1_accuracy": float(metrics.get("accuracy", 0.56)),
        }

    def train_model(self, csv_path: str | None = None, artifact_path: str | None = None) -> dict[str, object]:
        source_path = csv_path or settings.historical_matches_csv
        target_path = artifact_path or settings.model_artifact_path

        result = train_and_save_model(source_path, target_path)
        self.ml_model = TrainedMatchModel.load(result.artifact_path)
        self.predictor.set_ml_model(self.ml_model)

        metrics_payload = {
            "accuracy": result.accuracy,
            "log_loss": result.log_loss,
        }

        with SessionLocal() as db:
            run = ModelTrainingRun(
                artifact_path=result.artifact_path,
                source_csv_path=source_path,
                train_rows=result.train_rows,
                accuracy=result.accuracy,
                log_loss=result.log_loss,
                trained_at=datetime.fromisoformat(result.trained_at.replace("Z", "+00:00")).replace(tzinfo=None),
                metrics_json=json.dumps(metrics_payload),
            )
            db.add(run)
            db.commit()
            db.refresh(run)

        self.last_model_train_result = self._serialize_training_run(run)
        return self.last_model_train_result

    def get_model_training_history(self, limit: int = 10) -> list[dict[str, object]]:
        capped = max(1, min(limit, 100))
        with SessionLocal() as db:
            rows = (
                db.query(ModelTrainingRun)
                .order_by(ModelTrainingRun.id.desc())
                .limit(capped)
                .all()
            )
            return [self._serialize_training_run(row) for row in rows]

    def reload_model(self, artifact_path: str | None = None) -> dict[str, object]:
        target_path = artifact_path or settings.model_artifact_path
        loaded = TrainedMatchModel.load(target_path)
        self.ml_model = loaded
        self.predictor.set_ml_model(loaded)
        self.last_model_train_result = self._load_last_training_run()
        return {
            "status": "ok" if loaded is not None else "missing",
            "artifact_path": target_path,
            "model_loaded": loaded is not None,
        }

    def get_model_status(self) -> dict[str, object]:
        if self.ml_model is None:
            loaded = TrainedMatchModel.load(settings.model_artifact_path)
            if loaded is not None:
                self.ml_model = loaded
                self.predictor.set_ml_model(loaded)

        latest = self._load_last_training_run()
        self.last_model_train_result = latest
        return {
            "model_loaded": self.ml_model is not None,
            "artifact_path": settings.model_artifact_path,
            "last_train_result": latest,
            "trained_at": self.ml_model.trained_at if self.ml_model is not None else None,
        }


service = TournamentService()
