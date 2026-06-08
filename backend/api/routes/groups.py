from fastapi import APIRouter, HTTPException

from api.schemas import BulkGroupSetupPayload, GroupSetupPayload, ResultPayload
from tournament.service import service

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("")
def get_groups() -> dict[str, list[dict[str, int | float | str]]]:
    return service.get_groups()


@router.get("/standings")
def get_standings() -> dict[str, list[tuple[str, dict[str, int]]]]:
    return service.get_standings()


@router.get("/{group}/schedule")
def get_group_schedule(group: str) -> dict[str, object]:
    schedule = service.get_group_schedule(group)
    if not schedule:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"group": group.upper(), "matches": schedule}


@router.get("/{group}/standings")
def get_group_standings(group: str) -> dict[str, object]:
    standings = service.get_group_standings(group)
    if not standings:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"group": group.upper(), "standings": standings}


@router.post("/setup")
def setup_group(payload: GroupSetupPayload) -> dict[str, str]:
    service.set_group_teams(payload.group, [team.model_dump() for team in payload.teams])
    return {"status": "ok"}


@router.post("/setup-all")
def setup_all_groups(payload: BulkGroupSetupPayload) -> dict[str, str]:
    service.set_all_groups({group: [team.model_dump() for team in teams] for group, teams in payload.groups.items()})
    return {"status": "ok"}


@router.post("/result")
def submit_result(payload: ResultPayload) -> dict[str, object]:
    standings = service.add_result(
        payload.group,
        payload.home,
        payload.away,
        payload.homeGoals,
        payload.awayGoals,
    )
    return {"group": payload.group.upper(), "standings": standings}
