# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, fields, models, tools, _
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class DistributionListLine(models.Model):
    _name = "distribution.list.line"
    _inherit = [
        'distribution.list.line',
        'mozaik.abstract.model',
    ]
    _order = 'name'
    _unicity_keys = 'name, company_id'

    @api.model
    def _src_model_id_domain(self):
        """

        :return: list of tuple (domain)
        """
        return [('model', 'in', [])]

    name = fields.Char(
        required=True,
        track_visibility='onchange',
    )
    domain = fields.Text(
        string="Expression",
        required=True,
        track_visibility='onchange',
    )
    src_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        index=True,
        track_visibility='onchange',
        domain=_src_model_id_domain,
    )

    @api.model_cr
    def init(self):
        """
        Drop the constraint about unique name
        :return:
        """
        result = super(DistributionListLine, self).init()
        tools.drop_constraint(
            self.env.cr, self._table, "unique_name_by_company")
        return result

    @api.multi
    def get_list_without_coordinate_from_domain(self):
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

    def action_invalidate(self, vals=None):
        """
        Invalidates distribution list Lines
        :param vals: dict
        :return: bool
        """
        vals = vals or {}
        vals.update({
            'distribution_list_in_ids': [(5, False, False)],
            'distribution_list_out_ids': [(5, False, False)],
        })
        return super(DistributionListLine, self).action_invalidate(vals=vals)
