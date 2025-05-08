from __future__ import annotations

import abc
from abc import ABC
from typing import Any, Type

from pydantic import BaseModel, ConfigDict, Field

from .link import Link
from .rating import Rating

STRUCTURAL_LINKS = ["self", "child", "parent", "root", "item"]


class StacObject(BaseModel, ABC):
    """All the fields shared by STAC objects

    We're very permissive so we can always deserialize.
    """

    model_config = ConfigDict(extra="allow")

    type: str | None = Field(default=None)
    stac_version: str = Field(default="1.0.0")
    id: str
    stac_extensions: list[str] = Field(default_factory=list)
    links: list[Link] = Field(default_factory=list)

    @classmethod
    def from_dict(cls: Type[StacObject], data: dict[str, Any]) -> StacObject:
        from .catalog import Catalog
        from .collection import Collection
        from .item import Item

        if type_ := data.get("type"):
            if type_ == "Catalog":
                return Catalog.model_validate(data)
            elif type_ == "Collection":
                return Collection.model_validate(data)
            elif type_ == "Feature":
                return Item.model_validate(data)
            else:
                raise ValueError(f"unknown type: {type_}")
        else:
            raise ValueError("no type set on STAC object")

    @abc.abstractmethod
    def get_file_name(self) -> str: ...

    def remove_structural_links(self) -> None:
        new_links = []
        canonical_link = None
        for link in self.links:
            if link.rel == "self":
                canonical_link = link.model_copy(update={"rel": "canonical"})
            if link.rel not in STRUCTURAL_LINKS:
                new_links.append(link)
        self.links = new_links
        if canonical_link:
            self.links.append(canonical_link)

    def set_link(self, link: Link) -> None:
        links = [k for k in self.links if k.rel != link.rel]
        links.append(link)
        self.links = links

    @abc.abstractmethod
    def set_rating(self, rating: Rating) -> None: ...
