from heystac import Config


def test_root_node() -> None:
    Config().get_root_node()


def test_get_rater() -> None:
    Config().get_rater()
