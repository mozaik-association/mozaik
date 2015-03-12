# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from operator import attrgetter

from openerp import models, api
from openerp import fields as new_fields
from openerp.osv import orm, fields

TRIGGER_UNAUTHORIZED = [
    'email_coordinate_id', 'postal_coordinate_id', 'fix_coordinate_id',
    'fax_coordinate_id', 'mobile_coordinate_id'
]


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.one
    @api.depends(
        'postal_coordinate_ids.unauthorized',
        'email_coordinate_ids.unauthorized',
        'phone_coordinate_ids.unauthorized',
        'postal_coordinate_ids.is_main',
        'email_coordinate_ids.is_main',
        'phone_coordinate_ids.is_main',
        'postal_coordinate_ids.active',
        'email_coordinate_ids.active',
        'phone_coordinate_ids.active')
    def _compute_unauthorized(self):
        for f in TRIGGER_UNAUTHORIZED:
            if attrgetter('%s.unauthorized' % f)(self):
                self.unauthorized = True
                break

    unauthorized = new_fields.Boolean(
        string='Unauthorized', compute='_compute_unauthorized', store=True,
        help='Checked if one or more main coordinates are unauthorized')


class res_partner(orm.Model):

    _inherit = 'res.partner'

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

# data model

    _columns = {
        # relation fields
        'partner_is_subject_relation_ids': fields.one2many(
            'partner.relation', 'subject_partner_id',
            string='Subject Relations',
            domain=[('active', '=', True)], context={'force_recompute': True}),
        'partner_is_object_relation_ids': fields.one2many(
            'partner.relation', 'object_partner_id', string='Object Relations',
            domain=[('active', '=', True)], context={'force_recompute': True}),

        'partner_is_subject_relation_inactive_ids': fields.one2many(
            'partner.relation', 'subject_partner_id',
            string='Subject Relations', domain=[('active', '=', False)]),
        'partner_is_object_relation_inactive_ids': fields.one2many(
            'partner.relation', 'object_partner_id',
            string='Object Relations', domain=[('active', '=', False)]),
    }

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        Reset some fields to their initial values.
        """
        default = default or {}
        default.update({
            'partner_is_subject_relation_ids': [],
            'partner_is_object_relation_ids': [],
            'partner_is_subject_relation_inactive_ids': [],
            'partner_is_object_relation_inactive_ids': [],
        })
        res = super(
            res_partner,
            self).copy_data(
            cr,
            uid,
            ids,
            default=default,
            context=context)
        return res
