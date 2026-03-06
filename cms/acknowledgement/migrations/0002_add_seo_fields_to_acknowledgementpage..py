from decimal import Decimal
from django.db import migrations, models
from django.core.validators import MaxValueValidator, MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ("acknowledgement", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="acknowledgementpage",
            name="seo_change_frequency",
            field=models.IntegerField(
                verbose_name="SEO change frequency",
                default=5,  # Monthly
                choices=[
                    (1, "Always"),
                    (2, "Hourly"),
                    (3, "Daily"),
                    (4, "Weekly"),
                    (5, "Monthly"),
                    (6, "Yearly"),
                    (7, "Never"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="acknowledgementpage",
            name="seo_priority",
            field=models.DecimalField(
                verbose_name="SEO priority",
                default=Decimal("0.5"),
                max_digits=2,
                decimal_places=1,
                validators=[
                    MaxValueValidator(Decimal("1.0")),
                    MinValueValidator(Decimal("0.1")),
                ],
            ),
        ),
    ]
