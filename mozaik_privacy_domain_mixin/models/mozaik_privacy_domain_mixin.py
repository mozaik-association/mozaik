# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.osv.expression import AND
from odoo.tools.safe_eval import safe_eval

DEFAULT_DOMAIN = "[]"


class PrivacyDomainMixin(models.AbstractModel):
    _name = "mozaik.privacy.domain.mixin"
    _description = "Mixin adding privacy domain"

    domain = fields.Text(
        string="Target partners domain",
        help="Add a domain on partners model to limit the access to this record.",
        default=DEFAULT_DOMAIN,
    )
    domain_is_set = fields.Boolean(
        string="Domain is set",
        compute="_compute_domain_is_set",
        search="_search_domain_is_set",
    )

    def _search_domain_is_set(self, operator, value):
        """
        Cases supported are
        * operator in ['=', '!=']
        * value is a boolean
        """
        if operator not in [
            "=",
            "!=",
        ] or not isinstance(value, bool):
            raise ValueError(_("This operator/value is not supported"))
        if operator == "!=":
            value = not value
        if value:
            return [("domain", "!=", DEFAULT_DOMAIN)]
        return [("domain", "=", DEFAULT_DOMAIN)]

    @api.depends("domain")
    def _compute_domain_is_set(self):
        for record in self:
            record.domain_is_set = record.domain != DEFAULT_DOMAIN

    def _filter_allowed_for_partner(self, partner_id):
        """
        Filter the self recordset to keep only records for which partner verifies
        the domain
        """
        allowed_records = self.browse()
        for rec in self:
            if not rec.domain_is_set or self.env["res.partner"].search(
                AND([[("id", "=", partner_id)], safe_eval(rec.domain)])
            ):
                allowed_records |= rec
        return allowed_records
