# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PaymentLinkWizard(models.TransientModel):

    _inherit = "payment.link.wizard"

    def _compute_default_reference(self, involvement):
        return f"Donation - {involvement.involvement_category_id.name}"

    @api.model
    def default_get(self, fields):
        res = super(PaymentLinkWizard, self).default_get(fields)
        res_id = self._context.get("active_id")
        res_model = self._context.get("active_model")
        if res_id and res_model == "partner.involvement":
            record = self.env[res_model].browse(res_id)
            res.update(
                {
                    "description": record.reference,
                    "amount": record.amount,
                    "currency_id": self.env.company.currency_id.id,
                    "partner_id": record.partner_id.id,
                    "amount_max": record.amount,
                }
            )
        return res

    def _generate_link(self):
        res = super(PaymentLinkWizard, self)._generate_link()
        for payment_link in self:
            if payment_link.res_model == "partner.involvement":
                payment_link.link += "&involvement_id=%s" % payment_link.res_id
        return res
