# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VirtualPartnerMembership(models.Model):

    _inherit = "virtual.partner.membership"

    membership_int_instance_id = fields.Many2one(
        "int.instance", string="Membership Internal Instance", store=True
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
                    m.int_instance_id as membership_int_instance_id
                    """
        )
        return select
