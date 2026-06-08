from itertools import combinations


def generate_group_schedule(groups: dict[str, list[str]]) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    match_number = 1
    for group_name in sorted(groups.keys()):
        teams = groups[group_name]
        group_matches: list[dict[str, object]] = []
        for home, away in combinations(teams, 2):
            # A 4-team group always has 6 fixtures.
            matchday = (len(group_matches) // 2) + 1
            if matchday > 3:
                matchday = 3
            matches.append(
                {
                    "match_number": match_number,
                    "stage": "GROUP",
                    "group": group_name,
                    "home": home,
                    "away": away,
                    "matchday": matchday,
                }
            )
            group_matches.append(matches[-1])
            match_number += 1
    return matches


def _build_mini_table(
    tied_teams: set[str],
    results: list[dict[str, int | str]],
    fifa_ranking: dict[str, int],
) -> dict[str, dict[str, int]]:
    mini = {
        team: {"Pts": 0, "GF": 0, "GA": 0, "R": fifa_ranking.get(team, 999)}
        for team in tied_teams
    }
    for row in results:
        home = str(row["home"])
        away = str(row["away"])
        if home not in tied_teams or away not in tied_teams:
            continue
        hg = int(row["home_goals"])
        ag = int(row["away_goals"])

        mini[home]["GF"] += hg
        mini[home]["GA"] += ag
        mini[away]["GF"] += ag
        mini[away]["GA"] += hg

        if hg > ag:
            mini[home]["Pts"] += 3
        elif ag > hg:
            mini[away]["Pts"] += 3
        else:
            mini[home]["Pts"] += 1
            mini[away]["Pts"] += 1
    return mini


def calculate_standings(
    teams: list[str],
    results: list[dict[str, int | str]],
    fifa_ranking: dict[str, int] | None = None,
) -> list[tuple[str, dict[str, int]]]:
    ranking = fifa_ranking or {}
    table = {
        t: {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Pts": 0, "R": ranking.get(t, 999)}
        for t in teams
    }
    for row in results:
        home = str(row["home"])
        away = str(row["away"])
        hg = int(row["home_goals"])
        ag = int(row["away_goals"])

        table[home]["P"] += 1
        table[away]["P"] += 1
        table[home]["GF"] += hg
        table[home]["GA"] += ag
        table[away]["GF"] += ag
        table[away]["GA"] += hg

        if hg > ag:
            table[home]["W"] += 1
            table[away]["L"] += 1
            table[home]["Pts"] += 3
        elif ag > hg:
            table[away]["W"] += 1
            table[home]["L"] += 1
            table[away]["Pts"] += 3
        else:
            table[home]["D"] += 1
            table[away]["D"] += 1
            table[home]["Pts"] += 1
            table[away]["Pts"] += 1

    grouped: dict[tuple[int, int, int], list[str]] = {}
    for team, stats in table.items():
        key = (stats["Pts"], stats["GF"] - stats["GA"], stats["GF"])
        grouped.setdefault(key, []).append(team)

    sorted_keys = sorted(grouped.keys(), reverse=True)
    resolved_order: list[str] = []

    for key in sorted_keys:
        tied = grouped[key]
        if len(tied) == 1:
            resolved_order.extend(tied)
            continue

        mini = _build_mini_table(set(tied), results, ranking)
        tie_sorted = sorted(
            tied,
            key=lambda team: (
                mini[team]["Pts"],
                mini[team]["GF"] - mini[team]["GA"],
                mini[team]["GF"],
                -mini[team]["R"],
            ),
            reverse=True,
        )
        resolved_order.extend(tie_sorted)

    return [(team, table[team]) for team in resolved_order]
