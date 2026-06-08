from fastapi.testclient import TestClient
from pathlib import Path

from api.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_groups_exist() -> None:
    response = client.get("/api/groups")
    assert response.status_code == 200
    data = response.json()
    assert "A" in data
    assert len(data["A"]) == 4


def test_group_schedule_endpoint() -> None:
    response = client.get("/api/groups/A/schedule")
    assert response.status_code == 200
    payload = response.json()
    assert payload["group"] == "A"
    assert len(payload["matches"]) == 6


def test_group_standings_and_third_place_endpoints() -> None:
    first_group = client.get("/api/groups").json()["A"]
    team_a = first_group[0]["name"]
    team_b = first_group[1]["name"]

    result_response = client.post(
        "/api/groups/result",
        json={
            "group": "A",
            "home": team_a,
            "away": team_b,
            "homeGoals": 2,
            "awayGoals": 1,
        },
    )
    assert result_response.status_code == 200

    standings_response = client.get("/api/groups/A/standings")
    assert standings_response.status_code == 200
    standings_payload = standings_response.json()
    assert standings_payload["group"] == "A"
    assert len(standings_payload["standings"]) == 4

    third_place_response = client.get("/api/standings/third-place")
    assert third_place_response.status_code == 200
    third_payload = third_place_response.json()
    assert "top8" in third_payload
    assert "all" in third_payload
    assert len(third_payload["all"]) == 12


def test_refresh_endpoint() -> None:
    response = client.get("/api/data/refresh")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in ("ok", "skipped")
    assert "source" in payload
    assert "refreshed_at" in payload


def test_bracket_progression_after_knockout_results() -> None:
    r32_response = client.get("/api/bracket/r32")
    assert r32_response.status_code == 200
    r32_pairs = r32_response.json()["round_of_32"]
    assert len(r32_pairs) == 16

    submit_74 = client.post(
        "/api/bracket/matches/74/result",
        json={"homeScore": 1, "awayScore": 0},
    )
    assert submit_74.status_code == 200

    submit_77 = client.post(
        "/api/bracket/matches/77/result",
        json={"homeScore": 2, "awayScore": 1},
    )
    assert submit_77.status_code == 200

    bracket_response = client.get("/api/bracket")
    assert bracket_response.status_code == 200
    bracket = bracket_response.json()
    r16_match_89 = next(match for match in bracket["round_of_16"] if match["match_number"] == 89)
    assert isinstance(r16_match_89["home_team"], str)
    assert isinstance(r16_match_89["away_team"], str)


def test_knockout_draw_without_tiebreak_is_invalid() -> None:
    response = client.post(
        "/api/bracket/matches/73/result",
        json={"homeScore": 1, "awayScore": 1},
    )
    assert response.status_code == 400


def test_latest_simulation_endpoint_after_run() -> None:
    run_response = client.post("/api/simulation/run", json={"n": 500})
    assert run_response.status_code == 200

    latest_response = client.get("/api/simulation/latest")
    assert latest_response.status_code == 200
    payload = latest_response.json()
    assert payload["n_simulations"] == 500
    assert isinstance(payload["winner_probabilities"], dict)


def test_model_performance_endpoint() -> None:
    response = client.get("/api/predictions/performance")
    assert response.status_code == 200
    payload = response.json()
    assert payload["model_version"] in ("ensemble_v1_no_ml", "ensemble_v2_ml")
    assert payload["tracked_teams"] == 48


def test_model_status_endpoint() -> None:
    response = client.get("/api/model/status")
    assert response.status_code == 200
    payload = response.json()
    assert "model_loaded" in payload
    assert "artifact_path" in payload


def test_model_train_endpoint_with_synthetic_data(tmp_path: Path) -> None:
    csv_file = tmp_path / "historical.csv"
    teams = ["A", "B", "C", "D", "E", "F"]

    rows = ["date,home_team,away_team,home_score,away_score"]
    day = 1
    for cycle in range(25):
        for i, home in enumerate(teams):
            away = teams[(i + cycle + 1) % len(teams)]
            home_score = (cycle + i) % 4
            away_score = (cycle + i + 2) % 4
            rows.append(f"2023-01-{(day % 28) + 1:02d},{home},{away},{home_score},{away_score}")
            day += 1

    csv_file.write_text("\n".join(rows), encoding="utf-8")
    artifact_path = str(tmp_path / "model.joblib")

    response = client.post(
        "/api/model/train",
        json={
            "csvPath": str(csv_file),
            "artifactPath": artifact_path,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["train_rows"] >= 100

    status_response = client.get("/api/model/status")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["last_train_result"] is not None
    assert status_payload["last_train_result"]["artifact_path"] == artifact_path

    history_response = client.get("/api/model/history?limit=5")
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert len(history_payload["runs"]) >= 1
    assert history_payload["runs"][0]["artifact_path"] == artifact_path


