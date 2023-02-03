# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProcessPaymentReturn(models.TransientModel):
    """
    Wizard used to automatically process payment returns.
    """

    _name = "process.payment.return"
    _description = "Wizard to automatically process payment returns"

    payment_return_ids = fields.Many2many("payment.return", readonly=True)

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        context = self.env.context

        ids = (
            context.get("active_ids")
            or (context.get("active_id") and [context.get("active_id")])
            or []
        )
        res["payment_return_ids"] = [(6, 0, ids)]
        return res

    def process_payment_return(self):
        self.ensure_one()
        self.payment_return_ids._filter_and_process_refusal()
