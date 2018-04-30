# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class PartnerInvolvement(models.Model):

    _inherit = 'partner.involvement'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        '''
        if any, for automatic supporter, advance the partner's workflow
        '''
        res = super(PartnerInvolvement, self).create(vals)
        if res.involvement_category_id.automatic_supporter and \
                res.partner_id.membership_state_code in (
                    False, 'without_membership'):
            vals = self.env['membership.request']._get_status_values(
                's', date_from=res.creation_time)
            res.partner_id.write(vals)
        return res
