# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_sponsorship_product = fields.Boolean(
        "Is Sponsorship Subscription",
        help="This product will be given if the partner is sponsored.",
    )

    @api.constrains("is_sponsorship_product")
    def _check_unique_sponsorship_product(self):
        if (
            self.env["product.template"].search_count(
                [("is_sponsorship_product", "=", True)]
            )
            > 1
        ):
            raise ValidationError(
                _("Please configure max. 1 sponsorship subscription.")
            )
