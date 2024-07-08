from django.db.models import Manager
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from cms.snippets.models import Menu


class MenuResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["body"]

    @property
    def data(self) -> dict[str, list[dict] | None]:
        try:
            body = self.instance.body.get_prep_value()
        except AttributeError:
            body = None

        return {"active_menu": body}


class MenuSerializer(serializers.Serializer):
    @property
    def menu_manager(self) -> Manager:
        return self.context.get("menu_manager", Menu.objects)

    @property
    def data(self) -> dict[str, ReturnDict[str, str] | None]:
        """Gets the body associated with the currently active global banner information

        Args:
            `menu_manager`: The `MenuManager`
                used to query for records

        Returns:
            Dict representation the of the active menu.
            If no menu is active, then None is returned

        """
        active_menu = self.menu_manager.get_active_menu()
        serializer = MenuResponseSerializer(instance=active_menu)
        return serializer.data
