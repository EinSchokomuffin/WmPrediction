from fastapi import APIRouter, HTTPException

from api.schemas import ModelTrainPayload
from tournament.service import service

router = APIRouter(prefix="/api/model", tags=["model"])


@router.get("/status")
def get_model_status() -> dict[str, object]:
    return service.get_model_status()


@router.post("/reload")
def reload_model(artifactPath: str | None = None) -> dict[str, object]:
    return service.reload_model(artifactPath)


@router.post("/train")
def train_model(payload: ModelTrainPayload) -> dict[str, object]:
    try:
        return service.train_model(payload.csvPath, payload.artifactPath)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
