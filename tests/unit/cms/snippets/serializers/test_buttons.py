from cms.snippets.serializers import (
    ButtonSerializer,
    ExternalButtonSerializer,
)


class TestButtonSerializer:
    def test_can_serialize_payload(self):
        """
        Given a valid button model payload
        When this is serialized with a `ButtonSerializer`
        Then the correct validated data is returned
        """
        # Given
        text = "Download"
        loading_text = "Downloading"
        endpoint = "/api/bulkdownloads/v1"
        method = "POST"
        button_type = "DOWNLOAD"
        data = {
            "text": text,
            "loading_text": loading_text,
            "endpoint": endpoint,
            "method": method,
            "button_type": button_type,
        }

        # When
        serializer = ButtonSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data["text"] == text
        assert serializer.validated_data["loading_text"] == loading_text
        assert serializer.validated_data["endpoint"] == endpoint
        assert serializer.validated_data["method"] == method
        assert serializer.validated_data["button_type"] == button_type


class TestExternalButtonSerializer:
    def test_can_serialize_payload(self):
        """
        Given a valid external_button model payload
        When this is serialized with a `ExternalButtonSerializer`
        Then the correct validated data is returned
        """
        text = "Download"
        url = "https://www.google.com"
        button_type = "Primary"
        icon = "Download"
        data = {
            "text": text,
            "url": url,
            "button_type": button_type,
            "icon": icon,
        }

        # When
        serializer = ExternalButtonSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data["text"] == text
        assert serializer.validated_data["url"] == url
        assert serializer.validated_data["button_type"] == button_type
        assert serializer.validated_data["icon"] == icon
