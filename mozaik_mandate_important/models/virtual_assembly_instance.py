# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models


class VirtualAssemblyInstance(models.Model):

    _inherit = "virtual.assembly.instance"

    is_important = fields.Boolean("Important Mandates")

    @api.model
    def _get_select(self):
        res = super()._get_select()
        return res + ", '%(is_important)s as is_important'"

    @api.model
    def _get_query_parameters(self, parameter=False):
        res = super()._get_query_parameters(parameter)
        is_important = "assembly.is_important" if parameter == "ext" else "NULL"
        res["is_important"] = AsIs(is_important)
        return res
