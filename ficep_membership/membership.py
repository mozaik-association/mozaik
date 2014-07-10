# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tools import SUPERUSER_ID
from openerp.tools import logging
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class abstract_membership(orm.AbstractModel):

    def _get_instance_id(self, cr, uid, ids, name, arg, context=None):
        """
        ================
        _get_instance_id
        ================
        get instance_id of the partner for each ids
        """
        result = {i: False for i in ids}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.partner_id.int_instance_id and obj.partner_id.int_instance_id \
                                or False
        return result

    _name = 'abstract.membership'
    _inherit = ['abstract.ficep.model']
    _description = 'Abstract Membership'

    _rec_name = 'partner_id'

    _instance_store_triggers = {
        'membership.memberhip': (lambda self, cr, uid, ids, context=None: ids, [], 10),
     }

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True,
                                       domain=[('is_company', '=', False)], select=True),
        'membership_state_id': fields.many2one('membership.state', 'State', select=True),
        'int_instance_id': fields.function(_get_instance_id, type='many2one', relation='int.instance',
                                           string='Internal Instance', select=True,
                                           track_visibility='onchange', store=_instance_store_triggers),
    }

    _unicity_keys = 'partner_id'

    def name_get(self, cr, uid, ids, context=None):
        """
        Name: Partner's name
        """
        if not ids:
            return []
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            display_name = '%s' % record.partner_id.display_name
            res.append((record['id'], display_name))
        return res


class membership_membership(orm.Model):

    _name = 'membership.membership'
    _inherit = ['abstract.membership']
    _description = 'Membership'

    _columns = {
        'membership_history_ids': fields.one2many('membership.history', 'membership_id', \
                                                      string='Memberships historical', domain=[('active', '=', True)]),
        'membership_history_inactive_ids': fields.one2many('membership.history', 'membership_id', \
                                                               string='Memberships historical', domain=[('active', '=', False)]),
    }

# orm methods

    def create(self, cr, uid, vals, context=None):
        res_id = super(membership_membership, self).create(cr, uid, vals, context=context)
        self.update_history(cr, uid, [res_id], vals, context=context)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(membership_membership, self).write(cr, uid, ids, vals, context=context)
        if vals.get('state', False):
            self.update_history(cr, uid, ids, vals, context=context)
        return res

    def update_history(self, cr, uid, ids, vals, context=None):
        """
        ==============
        update_history
        ==============
        Create a new ``membership history`` for each ``ids``
        If the membership already has a current history
        then set ``current`` to False
        """
        if vals is None:
            vals = {}
        vals_copy = vals.copy()
        for membership in self.browse(cr, uid, ids, context=context):
            membership_history_obj = self.pool['membership.history']
            current_history_ids = membership_history_obj.search(cr, uid, [('partner_id', '=', membership.partner_id.id),
                                                                                  ('is_current', '=', True)], context=context)
            if current_history_ids:
                current_history = self.browse(cr, uid, current_history_ids[0], context=context)
                current_history.write({'is_current': False})

            vals_copy['membership_id'] = membership.id
            membership_history_obj.create(cr, uid, vals_copy, context=context)


class membership_history(orm.Model):

    _name = 'membership.history'
    _inherit = ['abstract.membership']
    _description = 'Membership History'

    _order = 'create_date desc'

    _columns = {
        'is_current': fields.boolean('Is Current'),
        'membership_id': fields.many2one('membership.membership', 'Membership', select=True, track_visibility='onchange'),
    }

    _defaults = {
         'is_current': True,
    }

    _unicity_keys = 'N/A'


class membership_state(orm.Model):

    _name = 'membership.state'
    _inherit = ['abstract.ficep.model']
    _description = 'Membership State'

    _columns = {
        'name': fields.char('Status', required=True, track_visibility='onchange'),
        'code': fields.char('Code', required=True, track_visibility='onchange'),
        'membership_ids': fields.one2many('membership.membership', 'membership_state_id',
                                           string='Memberships', domain=[('active', '=', True)]),
        'membership_inactive_ids': fields.one2many('membership.membership', 'membership_state_id',
                                           string='Memberships', domain=[('active', '=', False)]),
    }

    _unicity_keys = 'code'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
