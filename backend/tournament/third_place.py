def rank_third_place_teams(
    group_results: dict[str, list[tuple[str, dict[str, int]]]]
) -> list[tuple[str, str, dict[str, int]]]:
    thirds: list[tuple[str, str, dict[str, int]]] = []
    for group_name, standings in group_results.items():
        team_name, stats = standings[2]
        thirds.append((group_name, team_name, stats))

    sorted_thirds = sorted(
        thirds,
        key=lambda x: (x[2]["Pts"], x[2]["GF"] - x[2]["GA"], x[2]["GF"], -x[2]["R"]),
        reverse=True,
    )
    return sorted_thirds[:8]


def rank_all_third_place_teams(
    group_results: dict[str, list[tuple[str, dict[str, int]]]]
) -> list[tuple[str, str, dict[str, int]]]:
    thirds: list[tuple[str, str, dict[str, int]]] = []
    for group_name, standings in group_results.items():
        team_name, stats = standings[2]
        thirds.append((group_name, team_name, stats))

    return sorted(
        thirds,
        key=lambda x: (x[2]["Pts"], x[2]["GF"] - x[2]["GA"], x[2]["GF"], -x[2]["R"]),
        reverse=True,
    )
