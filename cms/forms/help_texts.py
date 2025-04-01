CONFIRMATION_SLUG_FIELD = """
The slug to associate with the post-submission page. Defaults to `confirmation`.
"""
CONFIRMATION_PANEL_TITLE_FIELD = """
The title to associate with the main panel on the post-submission page.
"""
CONFIRMATION_PANEL_TEXT_FIELD = """
The text to place within the main panel on the post-submission page.
"""
CONFIRMATION_BODY_FIELD = """
The main body of text to place on the post-submission page.
"""
ANNOUNCEMENT_BANNER_TITLE: str = """
The title to associate with the announcement. This must be provided.
"""

ANNOUNCEMENT_BANNER_BODY: str = """
A body of text to be displayed by the announcement. There is a limit of 255 characters for this field.
"""

ANNOUNCEMENT_BANNER_TYPE: str = """
The type to associate with the announcement. Defaults to `Information`.
"""

ANNOUNCEMENT_BANNER_IS_ACTIVE: str = """
Whether to activate this banner only on this individual page. 
Note that multiple page banners can be active on one page. Consider 
carefully if you need multiple announcements to be active at once as
this can have an impact on user experience of the dashboard page.
"""
