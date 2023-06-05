from rest_framework_api_key.models import APIKey

from metrics.data.managers.api_keys import CustomAPIKeyManager


class CustomAPIKey(APIKey):
    objects = CustomAPIKeyManager()
