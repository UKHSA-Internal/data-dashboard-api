from unittest import mock
from metrics.api.middleware import JwtDetectionMiddleware
from django.test import RequestFactory, TestCase
from django.http import HttpResponse


def get_response(request):
    return HttpResponse("OK")


class TestJwtDetectionMiddleware(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.middleware = JwtDetectionMiddleware(get_response)

    def test_returns_true_when_jwt_provided(self):
        """
        Given a mocked request with a JWT
        When the request is received
        Then the has_jwt property on the request is set to "True"
        """
        # Given
        request = self.factory.get("/testing", HTTP_AUTHORIZATION="Bearer abc.def.ghi")

        # When
        response = self.middleware(request)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTrue(request.has_jwt)

    def test_returns_false_when_no_jwt_provided(self):
        """
        Given a mocked request with no JWT
        When the request is received
        Then the has_jwt property on the request is set to "False"
        """
        # Given
        request = self.factory.get("/testing")

        # When
        response = self.middleware(request)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertFalse(request.has_jwt)
        
    def test_only_accepts_valid_prefix_for_jwt(self):
        """
        Given a mocked request with an invalid JWT prefix
        When the request is received
        Then the has_jwt property on the request is set to "False"
        """
        # Given
        request = self.factory.get("/testing", HTTP_AUTHORIZATION="JWT abc.def.ghi")

        # When
        response = self.middleware(request)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertFalse(request.has_jwt)
        
    def test_only_accepts_valid_format_for_jwt(self):
        """
        Given a mocked request with an invalid JWT token format
        When the request is received
        Then the has_jwt property on the request is set to "False"
        """
        # Given
        request = self.factory.get("/testing", HTTP_AUTHORIZATION="Bearer abc.def")

        # When
        response = self.middleware(request)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertFalse(request.has_jwt)
