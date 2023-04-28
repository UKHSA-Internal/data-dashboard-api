from cms.dashboard import wagtail_hooks


def test_register_icons_returns_correct_list_of_icons():
    """
    Given a list of icons
    When the wagtail hook `register_icons()` is called
    Then a list of icons is returned including the original icons
        as well as a list of additional custom icons
    """
    # Given
    original_icons = ["original_icon_1.svg", "original_icon_2.svg"]

    # When
    registered_icons = wagtail_hooks.register_icons(icons=original_icons)

    # Then
    expected_icons = original_icons + wagtail_hooks.ADDITIONAL_CUSTOM_ICONS
    assert registered_icons == expected_icons
