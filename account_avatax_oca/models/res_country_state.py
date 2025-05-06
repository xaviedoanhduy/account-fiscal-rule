from odoo import fields, models


class CountryState(models.Model):
    _inherit = "res.country.state"

    recalculate_tax_rate = fields.Boolean(default=False)
