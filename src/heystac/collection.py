from pydantic import Field

from .rating import Rating
from .stac_object import StacObject


class Collection(StacObject):
    """A STAC collection"""

    type: str = Field(default="Collection")
    rating: Rating | None = Field(default=None, alias="heystac:rating")

    def get_file_name(self) -> str:
        return "collection.json"

    def set_rating(self, rating: Rating) -> None:
        self.rating = rating
