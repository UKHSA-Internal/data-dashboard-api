"""
Contains the base metadata for fake models used in unit tests
"""


class FakeMeta:
    """
    This fake metadata ensure that we do not create new tables
    when inheriting production ones.

    """

    proxy = True
    app_label = "data"
