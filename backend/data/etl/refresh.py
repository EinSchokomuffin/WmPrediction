from __future__ import annotations

from collections import defaultdict

from data.clients.football_data import FootballDataClient


def _group_letter(group_name: str) -> str | None:
    normalized = group_name.strip().upper()
    if normalized.startswith("GROUP_") and len(normalized) == 7:
        return normalized[-1]
    if len(normalized) == 1 and "A" <= normalized <= "L":
        return normalized
    return None


def refresh_groups_from_football_data(
    current_groups: dict[str, list[dict[str, int | float | str]]],
) -> tuple[dict[str, list[dict[str, int | float | str]]], dict[str, str | int]]:
    client = FootballDataClient()
    if not client.api_key:
        return current_groups, {
            "status": "skipped",
            "source": "football-data.org",
            "reason": "FOOTBALL_DATA_API_KEY not configured",
            "updated_groups": 0,
        }

    standings_payload = client.fetch_world_cup_standings()
    groups_raw = standings_payload.get("standings", [])

    grouped_teams: dict[str, list[dict[str, int | float | str]]] = defaultdict(list)
    for group_block in groups_raw:
        group_label = str(group_block.get("group", ""))
        letter = _group_letter(group_label)
        if not letter:
            continue

        table = group_block.get("table", [])
        for row in table:
            team = row.get("team", {})
            name = str(team.get("name", "")).strip()
            if not name:
                continue
            grouped_teams[letter].append(
                {
                    "name": name,
                    "elo": 1500.0,
                    "fifaRanking": int(row.get("position", 999)),
                }
            )

    if not grouped_teams:
        return current_groups, {
            "status": "skipped",
            "source": "football-data.org",
            "reason": "No group standings returned",
            "updated_groups": 0,
        }

    merged = {**current_groups}
    updated = 0
    for group, teams in grouped_teams.items():
        if len(teams) == 4:
            merged[group] = teams
            updated += 1

    return merged, {
        "status": "ok",
        "source": "football-data.org",
        "updated_groups": updated,
    }
