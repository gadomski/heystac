from heystac import Catalog, Collection, Item


def test_get_file_name_catalog(catalog: Catalog) -> None:
    assert catalog.get_file_name() == "catalog.json"


def test_get_file_name_collection(collection: Collection) -> None:
    assert collection.get_file_name() == "collection.json"


def test_get_file_name_item(item: Item) -> None:
    assert item.get_file_name() == "the-item.json"


def test_get_file_name_with_slash(item: Item) -> None:
    item.id = "wow/this/is/bad"
    assert item.get_file_name() == "wow_this_is_bad.json"
