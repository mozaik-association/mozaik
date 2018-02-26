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
    ('n', 'Other'))


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

    request_type = fields.Selection(MEMBERSHIP_REQUEST_TYPE)

    @api.multi
    def validate_request(self):
        self.ensure_one()
        super(MembershipRequest, self).validate_request()
        self.distribution_list_ids.write({
            'opt_in_ids': [(4, self.partner_id.id)],
            'opt_out_ids': [(3, self.partner_id.id)],
        })
        return True

    def onchange_partner_id(self, cr, uid, ids,
                            is_company, request_type, partner_id,
                            technical_name, context=None):
        """
        Keep Other as request type when the partner is a company
        """
        res = super(MembershipRequest, self).onchange_partner_id(
            cr, uid, ids,
            is_company, request_type, partner_id,
            technical_name, context=context)

        if is_company and request_type == 'n':
            res['value']['request_type'] = 'n'

        return res
