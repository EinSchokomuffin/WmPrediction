from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.bracket import router as bracket_router
from api.routes.data import router as data_router
from api.routes.groups import router as groups_router
from api.routes.predictions import router as predictions_router
from api.routes.simulation import router as simulation_router
from api.routes.standings import router as standings_router
from core.config import settings
from core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups_router)
app.include_router(bracket_router)
app.include_router(predictions_router)
app.include_router(simulation_router)
app.include_router(standings_router)
app.include_router(data_router)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}
