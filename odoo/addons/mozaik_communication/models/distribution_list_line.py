# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.osv import expression


class DistributionListLine(models.Model):
    _name = "distribution.list.line"
    _inherit = [
        'distribution.list.line',
        'mozaik.abstract.model',
    ]
    _unicity_keys = 'name, company_id'

    @api.model
    def _get_src_model_name(self):
        """
        Get the list of available model name
        Intended to be inherited
        :return: list of string
        """
        return []

    @api.model
    def _src_model_id_domain(self):
        """

        :return: list of tuple (domain)
        """
        return [('model', 'in', self._get_src_model_name())]

    name = fields.Char(
        track_visibility='onchange',
    )
    domain = fields.Text(
        track_visibility='onchange',
    )
    src_model_id = fields.Many2one(
        track_visibility='onchange',
        domain=_src_model_id_domain,
    )

    @api.multi
    def result_without_coordinate_action(self):
        result = self._get_list_from_domain()
        result.update({
            'name': _('Result of %s filter without coordinate') % self.name
        })
        domain = result.get('domain', [])
        domain = expression.AND([domain, [('active', '=', False)]])
        result.update({
            'domain': domain,
        })
        return result
