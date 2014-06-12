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
from openerp.osv import orm, fields


class distribution_list(orm.Model):

    _name = "distribution.list"
    _inherit = ['distribution.list', 'abstract.ficep.model']

    def _get_user_id(self, cr, uid, ids=None, context=None):
        """
        ============
        _get_user_id
        ============
        Return user id value for many2many field
        """
        return [[6, False, [uid]]]

    _columns = {
        'name': fields.char(string='Name', required=True, track_visibility='onchange'),
        'res_users_ids': fields.many2many('res.users', 'dist_list_res_users_rel', id1='dist_list_id', id2='res_users_id', string='Users',
                                          required=True, select=True),
        'int_instance_id': fields.many2one('int.instance', 'Internal Instance', select=True, track_visibility='onchange'),
    }

    _defaults = {
        'res_users_ids': _get_user_id,
        'dst_model_id': lambda self, cr, uid, c:
        self.pool.get('ir.model').search(cr, uid, [('model', '=', 'virtual.target')], context=c)[0],
        'bridge_field': 'common_id',
    }


class distribution_list_line(orm.Model):

    _name = "distribution.list.line"
    _inherit = ['distribution.list.line', 'abstract.ficep.model']

    _columns = {
        'name': fields.char(string='Name', required=True, track_visibility='onchange'),
        'domain': fields.text(string="Expression", required=True, track_visibility='onchange'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
