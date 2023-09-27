# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerInvolvement(models.Model):
    _inherit = "virtual.partner.involvement"

    is_donor = fields.Boolean(
        string="Is a donor",
    )
    promise = fields.Boolean()

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = (
            super()._get_select()
            + """,
                p.is_donor,
                pi.promise AS promise"""
        )
        return select
