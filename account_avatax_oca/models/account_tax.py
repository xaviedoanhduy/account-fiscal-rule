from odoo import _, api, exceptions, fields, models


class AccountTax(models.Model):
    """Inherit to implement the tax using avatax API"""

    _inherit = "account.tax"

    is_avatax = fields.Boolean()

    @api.model
    def _get_avalara_tax_domain(self, tax_rate, doc_type, tax_name=None):
        domain = [
            ("amount", "=", tax_rate),
            ("is_avatax", "=", True),
            (
                "company_id",
                "=",
                self.env.company.id,
            ),
        ]
        if tax_name:
            domain.append(("name", "=", tax_name))
        return domain

    @api.model
    def _get_avalara_tax_name(self, tax_rate, doc_type=None):
        return _("{}%*").format(str(tax_rate))

    @api.model
    def get_avalara_tax(self, tax_rate, doc_type, tax_name=None):
        domain = self._get_avalara_tax_domain(tax_rate, doc_type, tax_name)
        tax = self.with_context(active_test=False).search(domain, limit=1)
        if tax and not tax.active:
            tax.active = True
        if not tax:
            domain = self._get_avalara_tax_domain(0, doc_type, "")
            tax_template = self.search(domain, limit=1)
            if not tax_template:
                raise exceptions.UserError(
                    _("Please configure Avatax Tax for Company %s:")
                    % self.env.company.name
                )
            # If you get a unique constraint error here,
            # check the data for your existing Avatax taxes.
            vals = {
                "amount": tax_rate,
                "name": tax_name
                if tax_name
                else self._get_avalara_tax_name(tax_rate, doc_type),
            }
            tax = tax_template.sudo().copy(default=vals)
            # Odoo core does not use the name set in default dict
            tax.name = vals.get("name")
        return tax
