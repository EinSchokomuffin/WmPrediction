from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split

FEATURE_NAMES = [
    "elo_diff",
    "elo_home",
    "elo_away",
    "ranking_diff",
    "home_form_points",
    "away_form_points",
    "home_goals_scored_5",
    "home_goals_conceded_5",
    "away_goals_scored_5",
    "away_goals_conceded_5",
]


@dataclass(frozen=True)
class TrainResult:
    artifact_path: str
    train_rows: int
    accuracy: float
    log_loss: float
    trained_at: str


class TrainedMatchModel:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.model = payload["model"]
        self.team_profiles = payload["team_profiles"]
        self.global_profile = payload["global_profile"]
        self.metrics = payload["metrics"]
        self.feature_names = payload["feature_names"]
        self.trained_at = payload["trained_at"]

    @classmethod
    def load(cls, artifact_path: str) -> TrainedMatchModel | None:
        path = Path(artifact_path)
        if not path.exists():
            return None
        payload = joblib.load(path)
        return cls(payload)

    def predict(
        self,
        home: str,
        away: str,
        home_elo: float,
        away_elo: float,
        home_rank: int,
        away_rank: int,
    ) -> dict[str, float]:
        home_profile = self.team_profiles.get(home, self.global_profile)
        away_profile = self.team_profiles.get(away, self.global_profile)

        row = {
            "elo_diff": home_elo - away_elo,
            "elo_home": home_elo,
            "elo_away": away_elo,
            "ranking_diff": float(home_rank - away_rank),
            "home_form_points": float(home_profile["form_points"]),
            "away_form_points": float(away_profile["form_points"]),
            "home_goals_scored_5": float(home_profile["goals_scored_5"]),
            "home_goals_conceded_5": float(home_profile["goals_conceded_5"]),
            "away_goals_scored_5": float(away_profile["goals_scored_5"]),
            "away_goals_conceded_5": float(away_profile["goals_conceded_5"]),
        }

        vector = np.array([[row[name] for name in self.feature_names]], dtype=float)
        probabilities = self.model.predict_proba(vector)[0]
        class_probabilities = {int(label): float(probabilities[idx]) for idx, label in enumerate(self.model.classes_)}

        return {
            "home_win_prob": class_probabilities.get(0, 0.0),
            "draw_prob": class_probabilities.get(1, 0.0),
            "away_win_prob": class_probabilities.get(2, 0.0),
        }


def _result_label(home_score: int, away_score: int) -> int:
    if home_score > away_score:
        return 0
    if home_score == away_score:
        return 1
    return 2


def _points_for_match(scored: int, conceded: int) -> int:
    if scored > conceded:
        return 3
    if scored == conceded:
        return 1
    return 0


def _update_elo(home_elo: float, away_elo: float, home_score: int, away_score: int) -> tuple[float, float]:
    k = 30.0
    expected_home = 1.0 / (1.0 + 10 ** ((away_elo - home_elo) / 400.0))
    expected_away = 1.0 - expected_home

    actual_home = 1.0 if home_score > away_score else 0.5 if home_score == away_score else 0.0
    actual_away = 1.0 - actual_home

    return (
        home_elo + k * (actual_home - expected_home),
        away_elo + k * (actual_away - expected_away),
    )


def train_and_save_model(csv_path: str, artifact_path: str) -> TrainResult:
    source_path = Path(csv_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Training CSV not found: {csv_path}")

    df = pd.read_csv(source_path)
    required = {"date", "home_team", "away_team", "home_score", "away_score"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Training CSV missing required columns: {sorted(missing)}")

    df = df.dropna(subset=["home_team", "away_team", "home_score", "away_score"]).copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    if len(df) < 100:
        raise ValueError("Training dataset is too small. Need at least 100 matches.")

    elo = defaultdict(lambda: 1500.0)
    rank = defaultdict(lambda: 100)

    history = defaultdict(
        lambda: {
            "points": deque(maxlen=5),
            "goals_for": deque(maxlen=5),
            "goals_against": deque(maxlen=5),
        }
    )

    rows: list[dict[str, float]] = []
    labels: list[int] = []

    for _, match in df.iterrows():
        home = str(match["home_team"]).strip()
        away = str(match["away_team"]).strip()
        home_score = int(match["home_score"])
        away_score = int(match["away_score"])

        home_hist = history[home]
        away_hist = history[away]

        row = {
            "elo_diff": float(elo[home] - elo[away]),
            "elo_home": float(elo[home]),
            "elo_away": float(elo[away]),
            "ranking_diff": float(rank[home] - rank[away]),
            "home_form_points": float(sum(home_hist["points"])),
            "away_form_points": float(sum(away_hist["points"])),
            "home_goals_scored_5": float(np.mean(home_hist["goals_for"])) if home_hist["goals_for"] else 0.0,
            "home_goals_conceded_5": float(np.mean(home_hist["goals_against"])) if home_hist["goals_against"] else 0.0,
            "away_goals_scored_5": float(np.mean(away_hist["goals_for"])) if away_hist["goals_for"] else 0.0,
            "away_goals_conceded_5": float(np.mean(away_hist["goals_against"])) if away_hist["goals_against"] else 0.0,
        }

        rows.append(row)
        labels.append(_result_label(home_score, away_score))

        home_hist["points"].append(_points_for_match(home_score, away_score))
        away_hist["points"].append(_points_for_match(away_score, home_score))
        home_hist["goals_for"].append(home_score)
        home_hist["goals_against"].append(away_score)
        away_hist["goals_for"].append(away_score)
        away_hist["goals_against"].append(home_score)

        elo[home], elo[away] = _update_elo(elo[home], elo[away], home_score, away_score)

    X = pd.DataFrame(rows, columns=FEATURE_NAMES)
    y = np.array(labels, dtype=int)

    class_labels = sorted(np.unique(y).tolist())
    if len(class_labels) < 2:
        raise ValueError("Training dataset must contain at least two outcome classes.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "log_loss": float(log_loss(y_test, probabilities, labels=list(model.classes_))),
    }

    team_profiles: dict[str, dict[str, float]] = {}
    for team, state in history.items():
        points = list(state["points"])
        gf = list(state["goals_for"])
        ga = list(state["goals_against"])
        team_profiles[team] = {
            "form_points": float(sum(points)),
            "goals_scored_5": float(np.mean(gf)) if gf else 0.0,
            "goals_conceded_5": float(np.mean(ga)) if ga else 0.0,
        }

    global_profile = {
        "form_points": float(np.mean([value["form_points"] for value in team_profiles.values()])) if team_profiles else 0.0,
        "goals_scored_5": float(np.mean([value["goals_scored_5"] for value in team_profiles.values()])) if team_profiles else 0.0,
        "goals_conceded_5": float(np.mean([value["goals_conceded_5"] for value in team_profiles.values()])) if team_profiles else 0.0,
    }

    target_path = Path(artifact_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    trained_at = datetime.now(UTC).isoformat()
    payload = {
        "model": model,
        "team_profiles": team_profiles,
        "global_profile": global_profile,
        "metrics": metrics,
        "feature_names": FEATURE_NAMES,
        "trained_at": trained_at,
    }
    joblib.dump(payload, target_path)

    return TrainResult(
        artifact_path=str(target_path),
        train_rows=len(X),
        accuracy=metrics["accuracy"],
        log_loss=metrics["log_loss"],
        trained_at=trained_at,
    )
