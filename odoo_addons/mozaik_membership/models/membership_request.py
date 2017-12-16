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
        digits=dp.get_precision('Product Price'), copy=False)
    reference = fields.Char(copy=False)
    effective_time = fields.Datetime(copy=False, string='Involvement Date')

    @api.multi
    def validate_request(self):
        """
        * create additional involvements
        * for new member, if any, save also its reference and amount
        * for donation, if any, save also its reference and amount
        """
        self.ensure_one()
        res = super(MembershipRequest, self).validate_request()

        # create new involvements
        current_categories = self.partner_id.partner_involvement_ids.mapped(
            'involvement_category_id')
        new_categories = self.involvement_category_ids.filtered(
            lambda s, cc=current_categories:
            s not in cc or s.allow_multi)
        for ic in new_categories:
            vals = {
                'partner_id': self.partner_id.id,
                'effective_time': self.effective_time,
                'involvement_category_id': ic.id,
            }
            if ic.involvement_type == 'donation':
                vals.update({
                    'reference': self.reference,
                    'amount': self.amount,
                })
            self.env['partner.involvement'].create(vals)

        # save membership amount
        if self.amount > 0.0 and self.reference:
            partner = self.partner_id
            if (self.membership_state_id.code == 'without_membership' and
                    partner.membership_state_code == 'member_candidate'):
                partner.write({
                    'reference': self.reference,
                    'amount': self.amount,
                })
        return res
