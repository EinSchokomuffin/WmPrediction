from fastapi import APIRouter, HTTPException

from api.schemas import KnockoutResultPayload
from tournament.service import service

router = APIRouter(prefix="/api/bracket", tags=["bracket"])


@router.get("")
def get_bracket() -> dict[str, list[dict[str, object]]]:
    return service.get_bracket()


@router.get("/r32")
def get_bracket_r32() -> dict[str, list[tuple[str, str | None]]]:
    return {"round_of_32": service.get_r32()}


@router.post("/matches/{match_number}/result")
def submit_knockout_result(match_number: int, payload: KnockoutResultPayload) -> dict[str, list[dict[str, object]]]:
    try:
        return service.submit_knockout_result(
            match_number=match_number,
            home_score=payload.homeScore,
            away_score=payload.awayScore,
            home_score_et=payload.homeScoreET,
            away_score_et=payload.awayScoreET,
            home_score_pen=payload.homeScorePen,
            away_score_pen=payload.awayScorePen,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
