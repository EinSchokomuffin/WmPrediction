from fastapi import APIRouter

from tournament.service import service

router = APIRouter(prefix="/api/standings", tags=["standings"])


@router.get("/third-place")
def get_third_place_standings() -> dict[str, list[tuple[str, str, dict[str, int]]]]:
    return service.get_third_place_ranking()
