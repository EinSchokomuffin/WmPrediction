from fastapi import APIRouter

from tournament.service import service

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/refresh")
@router.post("/refresh")
def refresh_data() -> dict[str, str | int]:
    return service.refresh_data()
