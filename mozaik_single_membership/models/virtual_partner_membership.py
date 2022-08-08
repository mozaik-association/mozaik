# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerMembership(models.Model):
    _inherit = "virtual.partner.membership"

    previous_membership_state_id = fields.Many2one(
        comodel_name="membership.state",
        string="Previous State",
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = (
            super()._get_select()
            + """,
                m.previous_state_id as previous_membership_state_id"""
        )
        return select
