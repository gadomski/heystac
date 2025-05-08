from heystac import Catalog, Context, rules


def test_validate_core(root: Catalog) -> None:
    context = Context()

    check = rules.validate_core(context, root)
    assert check
    assert check.score == 1

    root.stac_version = "not-a-real-version"
    check = rules.validate_core(context, root)
    assert check
    assert check.score == 0
