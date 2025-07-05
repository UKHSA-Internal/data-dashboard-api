import re

from wagtail import blocks


class HyphenatedFilterName(blocks.CharBlock):
    def clean(self, value):
        value = super().clean(value)
        value = value.strip().lower()
        value = re.sub(r"[\s_]+", "-", value)
        return re.sub(r"[^a-z0-9]-", "", value)
