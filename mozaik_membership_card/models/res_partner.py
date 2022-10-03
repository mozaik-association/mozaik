# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    membership_card_sent = fields.Boolean()
    membership_card_sent_date = fields.Date()

    @api.onchange("membership_card_sent")
    def _onchange_membership_card_sent_date(self):
        for rec in self:
            if rec.membership_card_sent:
                rec.membership_card_sent_date = fields.Date.today()
            else:
                rec.membership_card_sent_date = False
