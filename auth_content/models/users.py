from cms.dynamic_content.blocks import PermissionSetChoiceBlock
from django.db import models
from django.core.validators import RegexValidator
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel


class User(models.Model):
    user_entra_id = models.CharField(
        validators=[
            RegexValidator(
                regex="^[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$"
            )
        ],
    )
    
    permission_set = StreamField(
        [
            ("section", PermissionSetChoiceBlock()),
            
        ],
        use_json_field=True,
        
    )

    panels = [
        FieldPanel("user_entra_id"),
        FieldPanel("permission_set"),
    ]
