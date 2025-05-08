from pydantic import Field

from .rating import Rating
from .rule import Rule, Weights
from .stac_object import StacObject


class Catalog(StacObject):
    """A STAC catalog"""

    type: str = Field(default="Catalog")
    title: str | None = Field(default=None)
    rating: Rating | None = Field(default=None, alias="heystac:rating")
    rules: dict[str, Rule] | None = Field(default=None, alias="heystac:rules")
    weights: Weights | None = Field(default=None, alias="heystac:weights")

    def get_file_name(self) -> str:
        return "catalog.json"

    def set_rating(self, rating: Rating) -> None:
        self.rating = rating
