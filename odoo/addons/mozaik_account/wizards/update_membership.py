# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class UpdateMembership(models.TransientModel):

    _inherit = "update.membership"

    @api.multi
    def _prepare_update_product_price(self):
        """
        Add paid value to the dictionary
        """
        self.ensure_one()
        vals = super()._prepare_update_product_price()
        paid = self.membership_line_id._get_paid_based_on_price(self.price)
        vals['paid'] = paid
        return vals
