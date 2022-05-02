# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AbstractMandate(models.AbstractModel):

    _inherit = "abstract.mandate"

    no_show_on_website = fields.Boolean(
        string="Don't show this mandate", help="Don't show this mandate on website."
    )
    partner_no_show_on_website = fields.Boolean(
        string="Don't show partner mandates",
        help="Don't show any mandate from this partner on website.",
        related="partner_id.no_show_mandates",
    )

    @api.onchange("mandate_category_id")
    def _onchange_mandate_category_id(self):
        self.ensure_one()
        if self.mandate_category_id:
            self.no_show_on_website = self.mandate_category_id.no_show_on_website
