from heystac import Catalog, Config, Node


def test_rater_rate_node(catalog: Catalog) -> None:
    rater = Config().get_rater()
    rater.rate_node(Node(catalog))
