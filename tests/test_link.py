from heystac import Link


def test_clean_href() -> None:
    link = Link(href=".././parent.json", rel="parent")
    link.clean_href()
    assert link.href == "../parent.json"
