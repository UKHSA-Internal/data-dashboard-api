from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class LenientStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False
