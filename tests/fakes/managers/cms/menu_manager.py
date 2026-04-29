from cms.snippets.managers.menu import MenuManager, SimpleMenuManager
from cms.snippets.models.menu_builder import Menu, SimpleMenu


class FakeMenuManager(MenuManager):
    """
    A fake version of the `MenuManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, menus: list[Menu], **kwargs):
        self.menus = menus
        super().__init__(**kwargs)

    def get_active_menu(self) -> Menu | None:
        try:
            return next(menu for menu in self.menus if menu.is_active is True)
        except StopIteration:
            return None


class FakeSimpleMenuManager(SimpleMenuManager):
    """
    A fake version of the `SimpleMenuManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, menus: list[SimpleMenu], **kwargs):
        self.menus = menus
        super().__init__(**kwargs)

    def get_active_menu(self) -> Menu | None:
        try:
            return next(menu for menu in self.menus if menu.is_active is True)
        except StopIteration:
            return None
