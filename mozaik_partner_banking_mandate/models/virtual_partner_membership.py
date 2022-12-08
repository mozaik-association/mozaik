# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VirtualPartnerMembership(models.Model):

    _inherit = "virtual.partner.membership"

    has_valid_mandate = fields.Boolean(string="Has Valid Mandate")

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = (
            super()._get_select()
            + """,
                p.has_valid_mandate"""
        )
        return select
