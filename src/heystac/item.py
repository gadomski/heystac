from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field

from .rating import Rating
from .stac_object import StacObject


class Properties(BaseModel):
    """Item properties"""

    model_config = ConfigDict(extra="allow")

    dt: datetime.datetime | None = Field(
        alias="datetime", default_factory=datetime.datetime.now
    )
    rating: Rating | None = Field(default=None, alias="heystac:rating")


class Item(StacObject):
    """A STAC item"""

    type: str = Field(default="Feature")
    properties: Properties = Field(default_factory=Properties)

    def get_file_name(self) -> str:
        return self.id.replace("/", "_") + ".json"

    def set_rating(self, rating: Rating) -> None:
        self.properties.rating = rating


class ItemCollection(BaseModel):
    features: list[Item]
