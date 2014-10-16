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
from openerp.osv import orm, fields


class distribution_list(orm.Model):

    _name = "distribution.list"
    _inherit = ['distribution.list', 'mozaik.abstract.model']

    _columns = {
        'name': fields.char(
            string='Name', required=True, track_visibility='onchange'),
        'public': fields.boolean('Public', track_visibility='onchange'),
        'res_users_ids': fields.many2many(
            'res.users', 'dist_list_res_users_rel',
            id1='dist_list_id', id2='res_users_id',
            string='Owners', required=True),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance',
            select=True, track_visibility='onchange'),
    }

    _defaults = {
        'res_users_ids': lambda self, cr, uid, c: [uid],
        'dst_model_id': lambda self, cr, uid, c:
            self.pool['ir.model'].search(
                cr, uid, [('model', '=', 'virtual.target')])[0],
        'bridge_field': 'common_id',
        'partner_path': 'partner_id',
    }

# constraints

    # No More Unique Name For distribution list
    _sql_constraints = [('unique_name_by_company', 'check(1=1)', '')]

    _unicity_keys = 'name, int_instance_id'

# view methods: onchange, button

    def onchange_dst_model(self, cr, uid, ids, dst_model_id, context=None):
        res = {}
        bridge_field = False
        if dst_model_id:
            model = self.pool.get('ir.model').browse(
                cr, uid, dst_model_id, context=context)
            if model.model == 'res.partner':
                bridge_field = 'id'
            else:
                bridge_field = 'common_id'
        res['value'] = {'bridge_field': bridge_field}
        return res

# public methods

    def get_distribution_list_from_filters(self, cr, uid, ids, context=None):
        domain = [
            '|',
            ('to_include_distribution_list_line_ids', 'in', ids),
            ('to_exclude_distribution_list_line_ids', 'in', ids),
        ]
        res_ids = self.search(cr, uid, domain, context=context)
        return res_ids


class distribution_list_line(orm.Model):

    _name = "distribution.list.line"
    _inherit = ['distribution.list.line', 'mozaik.abstract.model']

    _columns = {
        'name': fields.char(
            string='Name', required=True, track_visibility='onchange'),
        'domain': fields.text(
            string='Expression', required=True, track_visibility='onchange'),
        'src_model_id': fields.many2one(
            'ir.model', string='Model', required=True, select=True,
            domain=[('model', 'in', [
                'res.partner',
                'virtual.partner.instance',
                'virtual.partner.membership',
                'virtual.partner.event',
                'virtual.partner.relation',
                'virtual.partner.involvement',
                'virtual.partner.candidature',
                'virtual.partner.mandate',
                'virtual.partner.retrocession',
                'virtual.assembly.instance',
            ])],
            track_visibility='onchange'),
    }

# constraints

    # No More Unique Name For distribution list
    _sql_constraints = [('unique_name_by_company', 'check(1=1)', '')]

    _unicity_keys = 'name, company_id'

# orm methods

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        '''
        Prevent abusive modifications on filter used by some unauthorized
        distribution lists
        '''
        if operation in ['unlink', 'write']:
            dl_obj = self.pool['distribution.list']
            dl_ids = dl_obj.get_distribution_list_from_filters(
                cr, SUPERUSER_ID, ids, context=context)
            dl_obj.check_access_rule(
                cr, uid, dl_ids, operation, context=context)

        super(distribution_list_line, self).check_access_rule(
            cr, uid, ids, operation, context=context)
