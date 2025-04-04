from unittest import mock

from public_api.middleware import NoIndexNoFollowMiddleware


class TestNoIndexNoFollowMiddleware:
    def test_robots_tag_header_added_to_response(self):
        """
        Given a dummy response
        When `process_response()` is called
            from the custom Django `NoIndexNoFollowMiddleware`
        Then the returned response contains
            the "X-Robots-Tag" header set to "noindex, nofollow"
        """
        # Given
        fake_response = {}

        # When
        mutated_response = NoIndexNoFollowMiddleware.process_response(
            request=mock.Mock(), response=fake_response
        )

        # Then
        assert mutated_response["X-Robots-Tag"] == "noindex, nofollow"
