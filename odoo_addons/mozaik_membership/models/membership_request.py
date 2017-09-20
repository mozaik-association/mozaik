# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MembershipRequest(models.Model):

    _inherit = 'membership.request'

    involvement_category_ids = fields.Many2many(
        'partner.involvement.category',
        relation='membership_request_involvement_category_rel',
        column1='request_id', column2='category_id',
        string='Involvement Categories')

    @api.multi
    def validate_request(self):
        """
        First check if the relations are set. For those try to update
        content
        In Other cases then create missing required data
        """
        self.ensure_one()
        res = super(MembershipRequest, self).validate_request()
        current_categories = self.partner_id.partner_involvement_ids.mapped(
            'partner_involvement_category_id')
        new_categories = [
            ic.id
            for ic in self.involvement_category_ids
            if ic not in current_categories
        ]
        vals = {'partner_id': self.partner_id.id}
        for ic_id in new_categories:
            vals['partner_involvement_category_id'] = ic_id
            self.env['partner.involvement'].create(vals)
        return res
