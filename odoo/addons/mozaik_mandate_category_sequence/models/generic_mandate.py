# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class GenericMandate(models.Model):

    _inherit = 'generic.mandate'
    _order = 'partner_id, sequence, mandate_category_id'

    sequence = fields.Integer(string="Protocolary weight")

    def _join_mandate(self):
        res = super()._join_mandate()
        res += """
        JOIN mandate_category AS mc
          ON mc.id = mandate.mandate_category_id
        """
        return res

    def _select_mandate(self):
        res = super()._select_mandate()
        res += """,
        mc.sequence
        """
        return res
