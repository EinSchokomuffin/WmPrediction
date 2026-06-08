from pydantic import BaseModel, Field


class TeamInput(BaseModel):
    name: str = Field(min_length=2)
    elo: float = Field(default=1500.0, ge=1000.0, le=2500.0)
    fifaRanking: int = Field(default=999, ge=1, le=999)


class GroupSetupPayload(BaseModel):
    group: str = Field(min_length=1, max_length=1)
    teams: list[TeamInput] = Field(min_length=4, max_length=4)


class ResultPayload(BaseModel):
    group: str = Field(min_length=1, max_length=1)
    home: str
    away: str
    homeGoals: int = Field(ge=0, le=20)
    awayGoals: int = Field(ge=0, le=20)


class MatchPredictionResponse(BaseModel):
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    expected_home_goals: float
    expected_away_goals: float
    confidence: float


class SimulationPayload(BaseModel):
    n: int = Field(default=1000, ge=100, le=50000)


class LatestSimulationResponse(BaseModel):
    created_at: str | None
    n_simulations: int
    winner_probabilities: dict[str, float]


class TeamTournamentProbsResponse(BaseModel):
    team: str
    winner_prob: float
    final_prob: float
    semi_final_prob: float
    quarter_final_prob: float
    round_of_16_prob: float
    group_advance_prob: float


class KnockoutResultPayload(BaseModel):
    homeScore: int = Field(ge=0, le=20)
    awayScore: int = Field(ge=0, le=20)
    homeScoreET: int | None = Field(default=None, ge=0, le=20)
    awayScoreET: int | None = Field(default=None, ge=0, le=20)
    homeScorePen: int | None = Field(default=None, ge=0, le=30)
    awayScorePen: int | None = Field(default=None, ge=0, le=30)


class ModelTrainPayload(BaseModel):
    csvPath: str | None = None
    artifactPath: str | None = None
