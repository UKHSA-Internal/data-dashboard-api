from cms.whats_new.serializers import BadgeSerializer


class TestBadgeSerializer:
    def test_can_serialize_payload(self):
        """
        Given a valid payload containing text and a colour
        When this is serialized with a `BadgeSerializer`
        Then the correct validated data is returned
        """
        # Given
        text = "DATE ISSUE"
        colour = "GREY"
        data = {"text": text, "colour": colour}

        # When
        serializer = BadgeSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data["text"] == text
        assert serializer.validated_data["colour"] == colour
