# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.addons.mozaik_membership import membership_request


MEMBERSHIP_REQUEST_TYPE = membership_request.MEMBERSHIP_REQUEST_TYPE.append(
    ('n', 'Newsletter'))


class MembershipRequest(models.Model):
    _name = 'membership.request'
    _inherit = ['membership.request']

    def _get_status_values(self, request_type):
        vals = super(MembershipRequest, self)._get_status_values(request_type)
        if request_type == 'n':
            vals.pop('accepted_date')
        return vals

    distribution_list_id = fields.Many2one(comodel_name='distribution.list',
                                           string='Distribution List',
                                           domain=[('newsletter', '=', True)]
                                           )
    request_type = fields.Selection(MEMBERSHIP_REQUEST_TYPE)

    @api.one
    def validate_request(self):
        super(MembershipRequest, self).validate_request()
        if self.request_type == 'n':
            vals = {}
            if self.partner_id not in self.distribution_list_id.opt_in_ids:
                vals['opt_in_ids'] = [(4, self.distribution_list_id.id)]
            if self.partner_id in self.distribution_list_id.opt_out_ids:
                vals['opt_out_ids'] = [(3, self.distribution_list_id.id)]
            if vals:
                self.partner_id.write(vals)
        return True

    def onchange_partner_id(self, cr, uid, ids,
                            is_company, request_type, partner_id,
                            technical_name, context=None):
        """
        Keep Newsletter when the partner is a company
        """
        res = super(MembershipRequest, self).onchange_partner_id(
            cr, uid, ids,
            is_company, request_type, partner_id,
            technical_name, context=context)

        if is_company and request_type == 'n':
            res['value']['request_type'] = 'n'

        return res
