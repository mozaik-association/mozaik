# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MassMailing(models.Model):
    _inherit = "mailing.mailing"

    create_uid = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
    )
    mailing_model = fields.Char(
        default="res.partner",
    )

    @api.model
    def _get_mailing_model(self):
        """
        Remove last insert: `mail.mass_mailing.contact`
        :return:
        """
        result = super()._get_mailing_model()
        if result:
            # remove last insert: mailing list
            result.pop()
        return result
