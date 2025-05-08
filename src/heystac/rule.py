from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class Rule(BaseModel):
    description: str
    importance: Importance
    function: str


class Importance(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Weights(BaseModel):
    high: int
    medium: int
    low: int
