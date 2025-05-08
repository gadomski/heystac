from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterator

from .catalog import Catalog
from .collection import Collection
from .item import Item
from .link import Link


class Node:
    """A node in a STAC catalog"""

    @classmethod
    def read_from(cls: type[Node], path: Path) -> Node:
        with open(path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("json data is not a dictionary")
        type_ = data["type"]
        if type_ == "Catalog":
            node = Node(Catalog.model_validate(data))
        elif type_ == "Collection":
            node = Node(Collection.model_validate(data))
        else:
            raise ValueError(
                f"cannot create a node from a dictionary with type={type_}"
            )
        node._resolve(path)
        return node

    def __init__(self, value: Catalog | Collection):
        self.value = value
        self.children: list[Node] = []
        self.items: list[Item] = []

    def _resolve(self, path: Path) -> Node:
        for child_link in self.child_links():
            child_path = (path.parent / child_link.href).resolve()
            child = Node.read_from(child_path)
            self.children.append(child)
        for item_link in self.item_links():
            item_path = (path.parent / item_link.href).resolve()
            with open(item_path) as f:
                item = Item.model_validate_json(f.read())
            self.items.append(item)
        self.remove_structural_links()
        return self

    def remove_structural_links(self) -> None:
        self.value.remove_structural_links()
        for child in self.children:
            child.remove_structural_links()
        for item in self.items:
            item.remove_structural_links()

    def add_or_replace_child(self, child: Node) -> None:
        children = []
        added = False
        for old_child in self.children:
            if child.value.id == old_child.value.id:
                added = True
                children.append(child)
            else:
                children.append(old_child)
        if not added:
            children.append(child)
        self.children = children

    def child_links(self) -> Iterator[Link]:
        for link in self.value.links:
            if link.rel == "child":
                yield link

    def item_links(self) -> Iterator[Link]:
        for link in self.value.links:
            if link.rel == "item":
                yield link

    def items_link(self) -> Link | None:
        return next((link for link in self.value.links if link.rel == "items"), None)

    def root_link(self) -> Link | None:
        return next((link for link in self.value.links if link.rel == "root"), None)

    def write_to(
        self, directory: Path, *, indent: int | None = 2, rewrite: bool = False
    ) -> None:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=False)
        elif rewrite:
            shutil.rmtree(directory)
            directory.mkdir(parents=True, exist_ok=False)
        file_name = self.value.get_file_name()

        root_link = self.root_link()
        if root_link is None:
            self.value.links.append(Link(href="./" + file_name, rel="root"))
            child_root_link = Link(href="../" + file_name, rel="root")
        else:
            child_root_link = Link(href="../" + root_link.href, rel="root")
        child_root_link.clean_href()

        for child in self.children:
            child_file_name = child.value.get_file_name()

            self.value.links.append(
                Link(href=f"./{child.value.id}/{child_file_name}", rel="child")
            )
            child.value.links.append(Link(href=f"../{file_name}", rel="parent"))
            child.value.links.append(child_root_link)

            child_directory = directory / child.value.id
            child.write_to(child_directory)

        for item in self.items:
            assert (
                file_name == "collection.json"
            ), "catalogs with items aren't supported"

            item_file_name = item.get_file_name()

            self.value.links.append(
                Link(
                    href=f"./{item_file_name}", rel="item", type="application/geo+json"
                )
            )
            item.links.append(Link(href=f"./{file_name}", rel="parent"))
            item.set_link(Link(href=f"./{file_name}", rel="collection"))
            item.links.append(child_root_link)

            with open(directory / item_file_name, "w") as f:
                f.write(
                    item.model_dump_json(
                        indent=indent, by_alias=True, exclude_none=True
                    )
                )

        with open(directory / file_name, "w") as f:
            f.write(
                self.value.model_dump_json(
                    indent=indent, by_alias=True, exclude_none=True
                )
            )

    def is_catalog(self) -> bool:
        return isinstance(self.value, Catalog)
