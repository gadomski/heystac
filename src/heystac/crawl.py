import tqdm
from httpx import Client
from pydantic import BaseModel

from .catalog import Catalog
from .collection import Collection
from .item import Item, ItemCollection
from .node import Node


class Crawler(BaseModel):
    href: str
    title: str | None
    id: str | None

    def crawl(self) -> Node:
        """Crawl and return the root node."""
        # TODO add heystac:crawled_at

        client = Client()

        response = client.get(self.href)
        response.raise_for_status()
        root = Catalog.model_validate(response.json())
        if self.title:
            root.title = self.title
        if self.id:
            root.id = self.id

        node = Node(root)
        child_links = list(node.child_links())
        progress_bar = tqdm.tqdm(total=len(child_links) * 2, desc=node.value.id)
        for child_link in child_links:
            # TODO allow deeper trees

            response = client.get(child_link.href)
            response.raise_for_status()
            collection = Collection.model_validate(response.json())
            progress_bar.update(1)
            child = Node(collection)

            if items_link := child.items_link():
                response = client.get(
                    items_link.href,
                    params=[("sortby", "-properties.datetime"), ("limit", 1)],
                )
                response.raise_for_status()
                item_collection = ItemCollection.model_validate(response.json())
                child.items.extend(item_collection.features)
            elif item_link := next(child.item_links(), None):
                response = client.get(item_link.href)
                response.raise_for_status()
                item = Item.model_validate(response.json())
                child.items.append(item)

            progress_bar.update(1)
            node.children.append(child)

        return node
