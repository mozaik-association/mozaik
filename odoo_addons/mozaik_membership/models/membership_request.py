# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

import openerp.addons.decimal_precision as dp


class MembershipRequest(models.Model):

    _inherit = 'membership.request'

    @api.model
    def _get_status_values(self, request_type):
        """
        :type request_type: char
        :param request_type: m or s for member or supporter.
            `False` if not defined
        :rtype: dict
        :rparam: affected date resulting of the `request_type`
            and the `status`
        """
        vals = {}
        if request_type:
            vals['accepted_date'] = fields.Date.today()
            if request_type == 'm':
                vals['free_member'] = False
            elif request_type == 's':
                vals['free_member'] = True
        return vals

    local_voluntary = fields.Boolean(track_visibility='onchange')
    regional_voluntary = fields.Boolean(track_visibility='onchange')
    national_voluntary = fields.Boolean(track_visibility='onchange')

    involvement_category_ids = fields.Many2many(
        'partner.involvement.category',
        relation='membership_request_involvement_category_rel',
        column1='request_id', column2='category_id',
        string='Involvement Categories')

    amount = fields.Float(
        digits=dp.get_precision('Product Price'),
        readonly=True, copy=False)
    reference = fields.Char(readonly=True, copy=False)

    @api.multi
    def validate_request(self):
        """
        * create additional involvements
        * for new member, if any, save also its reference
        """
        self.ensure_one()
        res = super(MembershipRequest, self).validate_request()
        current_categories = self.partner_id.partner_involvement_ids.mapped(
            'involvement_category_id')
        new_categories = [
            ic.id
            for ic in self.involvement_category_ids
            if ic not in current_categories
        ]
        vals = {'partner_id': self.partner_id.id}
        for ic_id in new_categories:
            vals['involvement_category_id'] = ic_id
            self.env['partner.involvement'].create(vals)
        if (self.membership_state_id.code == 'without_membership' and
                self.partner_id.membership_state_code == 'member_candidate' and
                self.amount > 0.0 and self.reference):
            self.partner_id.write({
                'reference': self.reference,
                'amount': self.amount,
            })
        return res
