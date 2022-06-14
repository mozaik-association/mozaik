# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AbstractVirtualModel(models.AbstractModel):

    _inherit = "abstract.virtual.model"

    partner_int_instance_id = fields.Many2one(
        "int.instance", string="Partner Internal Instance", store=True
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
                p.int_instance_id as partner_int_instance_id
                """
        )
        return select
