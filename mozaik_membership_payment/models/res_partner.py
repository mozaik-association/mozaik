# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    membership_line_payment_link = fields.Float(compute="_compute_ml_payment_link")

    def _compute_ml_payment_link(self):
        """
        Due to mozaik_single_instance, a partner can have max
        1 active membership line. We encode on the partner
        the payment_link of this membership.line
        """
        for record in self:
            record.membership_line_payment_link = False
            active_ml = record.membership_line_ids.filtered(lambda ml: ml.active)
            if active_ml:
                record.membership_line_payment_link = active_ml.payment_link
