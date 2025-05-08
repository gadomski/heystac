from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Check(BaseModel):
    rule_id: str
    score: Annotated[float, Field(strict=True, ge=0, le=1)]
    message: str | None = Field(default=None)
