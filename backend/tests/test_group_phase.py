from tournament.group_phase import calculate_standings


def test_calculate_standings_orders_by_points_and_goal_diff() -> None:
    teams = ["A", "B", "C", "D"]
    results = [
        {"home": "A", "away": "B", "home_goals": 2, "away_goals": 0},
        {"home": "C", "away": "D", "home_goals": 1, "away_goals": 1},
        {"home": "A", "away": "C", "home_goals": 1, "away_goals": 0},
        {"home": "B", "away": "D", "home_goals": 2, "away_goals": 1},
    ]

    standings = calculate_standings(teams, results)

    assert standings[0][0] == "A"
    assert standings[0][1]["Pts"] == 6
