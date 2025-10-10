def format_child_and_parent_theme_name(name: str) -> str:
    """Naming of themes can sometimes use a `-` rather than `_` in their naming
        This formats these strings to ensure `-` is replaced with `_` for
        selecting enums.

    Args:
        name: string containing either `parent_theme` or `child_theme`

    Returns:
        name: string with formatted `parent_theme` or `child_theme` name

    """
    return name.replace("-", "_").upper()
