from django.db import models


class ChangeFrequency(models.IntegerChoices):
    Always = 1
    Hourly = 2
    Daily = 3
    Weekly = 4
    Monthly = 5
    Yearly = 6
    Never = 7
