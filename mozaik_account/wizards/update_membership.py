# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class UpdateMembership(models.TransientModel):

    _inherit = "update.membership"

    update_type = fields.Selection(
        selection_add=[("price_paid", "Price Paid")],
        ondelete={"price_paid": "cascade"},
    )

    price_paid = fields.Float()

    def action_update(self):
        res = super().action_update()
        if self.update_type == "price_paid":
            res = self._update_price_paid()
        return res

    def _update_price_paid(self):
        """
        Update price_paid on membership.line
        :return: bool
        """
        self.ensure_one()
        return self.membership_line_id.write({"price_paid": self.price_paid})

    def _prepare_update_product_price(self):
        """
        Add paid value to the dictionary
        """
        self.ensure_one()
        vals = super()._prepare_update_product_price()
        paid = self.membership_line_id._price_is_zero(vals.get("price", 0.0))
        vals["paid"] = paid
        return vals
