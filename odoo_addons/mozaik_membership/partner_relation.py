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

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID


class partner_relation(orm.Model):

    _inherit = ['partner.relation']

    _sbj_int_instance_store_trigger = {
        'partner.relation': (
            lambda self, cr, uid, ids, context=None: ids,
            ['subject_partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['partner.relation'].search(
                            cr, SUPERUSER_ID,
                            [('subject_partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _obj_int_instance_store_trigger = {
        'partner.relation': (
            lambda self, cr, uid, ids, context=None: ids,
            ['object_partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['partner.relation'].search(
                            cr, SUPERUSER_ID,
                            [('object_partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'subject_instance_id': fields.related(
            'subject_partner_id', 'int_instance_id',
            string='Subject Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_sbj_int_instance_store_trigger),
        'object_instance_id': fields.related(
            'object_partner_id', 'int_instance_id',
            string='Object Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_obj_int_instance_store_trigger),
    }
