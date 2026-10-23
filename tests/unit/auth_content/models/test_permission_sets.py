from cms.auth_content.models.permission_sets import PermissionSet


class TestPermissionSet:
    def test_global_access_property_with_global_access(self):
        permission_set = PermissionSet()
        permission_set.theme = "-1"
        permission_set.geography_type = "-1"
        assert permission_set.global_access == True

    def test_global_access_property_without_global_access(self):
        permission_set = PermissionSet()
        permission_set.theme = "-1"
        permission_set.geography_type = "1"
        assert permission_set.global_access == False
