# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class MembershipRequest(models.Model):
    _name = 'membership.request'
    _inherit = ['membership.request']

    distribution_list_ids = fields.Many2many(
        comodel_name='distribution.list',
        relation='membership_request_distribution_list_rel',
        column1='request_id', column2='list_id',
        string='Newsletters',
        domain=[('newsletter', '=', True)],
    )
    request_type = fields.Selection(
        selection_add=[('n', 'Other')]
    )

    @api.multi
    def validate_request(self):
        self.ensure_one()
        result = super(MembershipRequest, self).validate_request()
        self.distribution_list_ids.write({
            'opt_in_ids': [(4, self.partner_id.id)],
            'opt_out_ids': [(3, self.partner_id.id)],
        })
        return result

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """
        Keep Other as request type when the partner is a company
        """
        force_request_type = False
        if self.is_company and self.request_type == 'n':
            force_request_type = True
        result = super(MembershipRequest, self)._onchange_partner_id()
        if force_request_type:
            self.request_type = 'n'
        return result
