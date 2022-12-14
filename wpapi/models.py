from tortoise.models import Model
from tortoise import fields


class MultiPathogen(Model):
    id = fields.IntField(pk=True)
    week = fields.IntField()
    year = fields.IntField()
    week_key = fields.CharField(max_length=7)
    publish_date = fields.DateField()
    season = fields.CharField(max_length=9, null=True)
    influenza_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    rsv_pct = fields.DecimalField(max_digits=3, decimal_places=1, null=True)
    rhinovirus_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    parainfluenza_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    hmpv_pct = fields.DecimalField(max_digits=3, decimal_places=1, null=True)
    adenovirus_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    sars_cov_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    influenza_a_h3n2_n_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    influenza_a_h1n1_pdm09_n_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    influenza_a_not_subtyped_n_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)
    influenza_b_n_pct = fields.DecimalField(
        max_digits=3, decimal_places=1, null=True)

    # Defining ``__str__`` is also optional, but gives you pretty
    # represent of model in debugger and interpreter
    def __str__(self):
        return f"Multipathogen data for {self.week_key}"
