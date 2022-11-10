from tortoise.models import Model
from tortoise import fields


class MultiPathogen(Model):
    id = fields.IntField(pk=True)
    week = fields.IntField()
    year = fields.IntField()
    week_key = fields.CharField(max_length=7)
    publish_date = fields.DateField()
    season = fields.CharField(max_length=9, null=True)
    influenza_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    rsv_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    rhinovirus_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    parainfluenza_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    hmpv_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    adenovirus_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    sars_cov_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    influenza_a_h3n2_n_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    influenza_a_h1n1_pdm09_n_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    influenza_a_not_subtyped_n_pct = fields.DecimalField(max_digits=3, decimal_places=1)
    influenza_b_n_pct = fields.DecimalField(max_digits=3, decimal_places=1)

    # Defining ``__str__`` is also optional, but gives you pretty
    # represent of model in debugger and interpreter
    def __str__(self):
        return f"Multipathogen data for {self.week_key}"

