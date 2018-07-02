# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from .res_partner import AVAILABLE_PARTNER_KINDS


class phone_coordinate(orm.Model):

    _name = 'phone.coordinate'
    _inherit = ['sub.abstract.coordinate', 'phone.coordinate']

    _update_track = {
        'is_main': {
            'mozaik_membership.main_phone_id_notification':
                lambda self, cr, uid, obj, ctx=None: obj.is_main,
            'mozaik_membership.former_phone_id_notification':
                lambda self, cr, uid, obj, ctx=None: not obj.is_main,
        },
        'expire_date': {
            'mozaik_membership.former_phone_id_notification':
                lambda self, cr, uid, obj, ctx=None: obj.expire_date,
        },
    }

    _int_instance_store_trigger = {
        'phone.coordinate': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['phone.coordinate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _partner_kind_store_trigger = {
        'phone.coordinate': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['phone.coordinate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        [
                            'is_assembly', 'is_company',
                            'identifier', 'membership_state_id'
                        ], 12),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
        'partner_kind': fields.related(
            'partner_id', 'kind', string='Partner Kind',
            type='selection', selection=AVAILABLE_PARTNER_KINDS,
            store=_partner_kind_store_trigger),
    }
