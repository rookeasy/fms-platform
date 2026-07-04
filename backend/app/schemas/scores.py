from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FppScoreRead(BaseModel):
    protectionScore: int = Field(ge=0, le=100)
    complianceScore: int = Field(ge=0, le=100)
    readinessScore: int = Field(ge=0, le=100)
    intelligenceScore: int = Field(ge=0, le=100)
    buildingHealthIndex: int = Field(ge=0, le=100)
    scoreDrivers: list[str]
    lastCalculatedAt: datetime
    targetType: str = "building"
    targetId: UUID | None = None
    buildingId: UUID | None = None


class PortfolioBuildingScoreRead(FppScoreRead):
    buildingName: str


class PortfolioScoresRead(BaseModel):
    protectionScore: int = Field(ge=0, le=100)
    complianceScore: int = Field(ge=0, le=100)
    readinessScore: int = Field(ge=0, le=100)
    intelligenceScore: int = Field(ge=0, le=100)
    buildingHealthIndex: int = Field(ge=0, le=100)
    scoreDrivers: list[str]
    lastCalculatedAt: datetime
    buildingCount: int
    buildings: list[PortfolioBuildingScoreRead]
