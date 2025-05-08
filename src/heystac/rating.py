from __future__ import annotations

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from .check import Check


class Rating(BaseModel):
    stars: Annotated[float, Field(strict=True, ge=0, le=5)]
    issues: Issues
    score: float
    total: int
    aggregate_score: float | None = Field(default=None)
    aggregate_total: int | None = Field(default=None)


class Issues(BaseModel):
    high: list[Check] = Field(default_factory=list)
    medium: list[Check] = Field(default_factory=list)
    low: list[Check] = Field(default_factory=list)
