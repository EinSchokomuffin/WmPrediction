from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Confederation(str, Enum):
    UEFA = "UEFA"
    CONMEBOL = "CONMEBOL"
    AFC = "AFC"
    CAF = "CAF"
    CONCACAF = "CONCACAF"
    OFC = "OFC"


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(1), unique=True, nullable=False)
    teams: Mapped[list["Team"]] = relationship(back_populates="group")


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    short_code: Mapped[str] = mapped_column(String(3), nullable=False)
    confederation: Mapped[Confederation | None] = mapped_column(SqlEnum(Confederation), nullable=True)
    fifa_ranking: Mapped[int] = mapped_column(Integer, default=999)
    elo_rating: Mapped[float] = mapped_column(Float, default=1500.0)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    group: Mapped[Group | None] = relationship(back_populates="teams")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_number: Mapped[int] = mapped_column(Integer, index=True)
    stage: Mapped[str] = mapped_column(String, index=True)
    home_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    away_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    home_win_prob: Mapped[float] = mapped_column(Float)
    draw_prob: Mapped[float] = mapped_column(Float)
    away_win_prob: Mapped[float] = mapped_column(Float)
    expected_home_goals: Mapped[float] = mapped_column(Float)
    expected_away_goals: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String, default="ensemble_v0")
