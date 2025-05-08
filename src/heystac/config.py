from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from .catalog import Catalog
from .node import Node
from .rate import Rater
from .rule import Rule, Weights


class Config(BaseSettings):
    """heystac configuration"""

    model_config = SettingsConfigDict(env_prefix="heystac_", toml_file="heystac.toml")

    catalog: LocalCatalogConfig = Field(default_factory=lambda: LocalCatalogConfig())
    root: Catalog = Field(default_factory=lambda: default_catalog())
    catalogs: dict[str, RemoteCatalogConfig] = Field(default_factory=dict)
    rules: dict[str, Rule] = Field(default_factory=lambda: default_rules())
    weights: Weights = Field(default_factory=lambda: default_weights())

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)

    def get_root_node(self) -> Node:
        if (catalog_path := self.catalog.path / "catalog.json").exists():
            root = Node.read_from(catalog_path)
        else:
            root = Node(self.root)
        assert isinstance(root.value, Catalog)
        root.value.rules = self.rules
        root.value.weights = self.weights
        return root

    def get_rater(self, exclude: list[str] | None = None) -> Rater:
        if exclude:
            rules = {id: rule for id, rule in self.rules.items() if id not in exclude}
        else:
            rules = self.rules
        return Rater(rules=rules, weights=self.weights)


class LocalCatalogConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: Path = Field(default_factory=lambda: Path("."))


class RemoteCatalogConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    href: str
    title: str


def default_catalog() -> Catalog:
    return Catalog(id="heystac-custom")


def default_rules() -> dict[str, Rule]:
    return {
        "validate-core": Rule(
            description="Validate the STAC object against its core json-schema",
            importance="high",
            function="heystac.rules:validate_core",
        ),
        "validate-geometry": Rule(
            description="Validate item geometries using shapely",
            importance="high",
            function="heystac.rules:validate_geometry",
        ),
        "links": Rule(
            description="Check that http and https links are accessible",
            importance="medium",
            function="heystac.rules:links",
        ),
        "validate-extensions": Rule(
            description="Validate the STAC object against all of its extension schemas",
            importance="medium",
            function="heystac.rules:validate_extensions",
        ),
        "version": Rule(
            description="Ensure the STAC version is v1.0.0 or v1.1.0",
            importance="medium",
            function="heystac.rules:version",
        ),
    }


def default_weights() -> Weights:
    return Weights(
        high=8,
        medium=2,
        low=1,
    )
