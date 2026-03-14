from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer


class TestCMSDraftPagesSerializer:
    def test_draft_serializer_is_normal_listable_serializer(self):
        """
        Given the draft page serializer
        When checking serializer identity
        Then it is exactly the normal pages serializer
        """
        assert CMSDraftPagesSerializer is ListablePageSerializer
