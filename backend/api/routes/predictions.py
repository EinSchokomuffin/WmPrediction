from fastapi import APIRouter, HTTPException

from api.schemas import MatchPredictionResponse, TeamTournamentProbsResponse
from tournament.service import service

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/match", response_model=MatchPredictionResponse)
def get_prediction(home: str, away: str) -> MatchPredictionResponse:
    try:
        return MatchPredictionResponse(**service.predict_match(home, away))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc


@router.get("/teams/{team_name}/tournament-probs", response_model=TeamTournamentProbsResponse)
def get_tournament_probs(team_name: str) -> TeamTournamentProbsResponse:
    return TeamTournamentProbsResponse(**service.get_team_tournament_probabilities(team_name))


@router.get("/performance")
def get_model_performance() -> dict[str, float | int | str]:
    return service.get_model_performance()
