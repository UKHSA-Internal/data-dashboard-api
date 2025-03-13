class ReadOnlyMixin:
    @classmethod
    def has_add_permission(cls, request):
        return False

    @classmethod
    def has_change_permission(cls, request):
        return False

    @classmethod
    def has_delete_permission(cls, request):
        return False
