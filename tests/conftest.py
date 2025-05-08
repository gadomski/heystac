from pathlib import Path

import pytest

from heystac import Catalog, Collection, Item


@pytest.fixture
def root(root_path: Path) -> Catalog:
    with open(root_path) as f:
        return Catalog.model_validate_json(f.read())


@pytest.fixture
def root_path() -> Path:
    return Path(__file__).parents[1] / "catalog" / "stac" / "catalog.json"


@pytest.fixture
def catalog() -> Catalog:
    return Catalog(id="the-catalog")


@pytest.fixture
def collection() -> Collection:
    return Collection(id="the-collection")


@pytest.fixture
def item() -> Item:
    return Item(id="the-item")
