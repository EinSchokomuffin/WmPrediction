from fastapi import APIRouter

from api.schemas import LatestSimulationResponse, SimulationPayload
from tournament.service import service

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.post("/run")
def run_simulation(payload: SimulationPayload) -> dict[str, dict[str, float]]:
    return {"winner_probabilities": service.run_simulation(payload.n)}


@router.post("/playout")
def run_tournament_playout() -> dict[str, object]:
    return service.simulate_tournament_playout()


@router.get("/latest", response_model=LatestSimulationResponse)
def get_latest_simulation() -> LatestSimulationResponse:
    return LatestSimulationResponse(**service.get_latest_simulation())
