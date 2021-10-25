# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.osv import expression


class DistributionListLine(models.Model):
    _name = "distribution.list.line"
    _inherit = [
        'mozaik.abstract.model',
        'distribution.list.line',
    ]
    _unicity_keys = 'N/A'

    name = fields.Char(
        tracking=True,
    )
    domain = fields.Text(
        tracking=True,
    )
    src_model_id = fields.Many2one(
        tracking=True,
    )

    def _get_target_recordset(self):
        """
        For excluding filters the result is transformed
        to exclude all target records linked
        to the concerned partners
        :return: target recordset
        """
        results = super()._get_target_recordset()
        partner_path = self.mapped('distribution_list_id').partner_path
        if results and all(self.mapped('exclude')) and partner_path:
            partners = results.mapped(partner_path)
            if partners:
                domain = [
                    (partner_path, 'in', partners.ids),
                ]
                results = results.search(domain)
        return results

    def action_show_filter_result_without_coordinate(self):
        """
        Show the result of the list without coordinate
        :return: dict/action
        """
        self.ensure_one()
        result = self.action_show_filter_result()
        result.update({
            'name': _('Result of %s without coordinate') % self.name
        })
        domain = result.get('domain', [])
        domain = expression.AND([domain, [('active', '=', False)]])
        result.update({
            'domain': domain,
        })
        return result
