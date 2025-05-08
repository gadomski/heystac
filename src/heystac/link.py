from pydantic import BaseModel, ConfigDict, Field


class Link(BaseModel):
    """A STAC link"""

    model_config = ConfigDict(extra="allow")

    href: str
    rel: str
    type: str = Field(default="application/json")

    def clean_href(self) -> None:
        self.href = self.href.replace("/./", "/")
