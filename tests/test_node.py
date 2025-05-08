from pathlib import Path

from heystac import Catalog, Collection, Item, Link, Node


def test_read_from(root_path: Path) -> None:
    Node.read_from(root_path)


def test_remove_structural_links(catalog: Catalog) -> None:
    catalog.links.append(Link(href="http://heystac.test/catalog.json", rel="root"))
    node = Node(catalog)
    node.remove_structural_links()
    assert not node.value.links


def test_add_or_replace_child(catalog: Catalog, collection: Collection) -> None:
    node = Node(catalog)
    node.add_or_replace_child(Node(collection.model_copy()))
    assert len(node.children) == 1
    node.add_or_replace_child(Node(collection))
    assert len(node.children) == 1


def test_write_to(tmp_path: Path, catalog: Catalog) -> None:
    node = Node(catalog)
    node.write_to(tmp_path)
    node = Node.read_from(tmp_path / "catalog.json")


def test_write_to_with_link(
    tmp_path: Path, catalog: Catalog, collection: Collection
) -> None:
    assert collection.id == "the-collection"

    node = Node(catalog)
    node.add_or_replace_child(Node(collection))
    node.write_to(tmp_path)
    with open(tmp_path / "catalog.json") as f:
        catalog = Catalog.model_validate_json(f.read())
    child_link = next(Node(catalog).child_links())
    assert child_link.href == "./the-collection/collection.json"


def test_dont_rewrite_items(tmp_path: Path, collection: Collection, item: Item) -> None:
    node = Node(collection)
    node.items.append(item)
    node.write_to(tmp_path)
    node = Node.read_from(tmp_path / "collection.json")
    assert len(node.items) == 1
    node.write_to(tmp_path)
    node = Node.read_from(tmp_path / "collection.json")
    assert len(node.items) == 1
