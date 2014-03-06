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
# System imports

# Other utilities imports

# OpenERP imports
import openerp
from openerp.osv import orm, fields
from openerp.tools.translate import _

# Local imports

# Constants
XXX_AVAILABLE_TYPES = [
                       ('xx', 'X'),
                       ('yy', 'Y'),
                      ]

xxx_available_types = dict(XXX_AVAILABLE_TYPES)


class res_partner_title(orm.Model):
    _inherit = 'res.partner.title'

    def create(self, cr, uid, vals, context=None):
        res = super(res_partner_title, self).create(cr, uid, vals, context=context)
        return res

class res_partner(orm.Model):

    _inherit = 'res.partner'

class xxxx(orm.Model):

    _name = 'xxx'
    _description = "XXX"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

# static methods
    def _your_field_function(self):
        pass

    def _your_selection_function(self):
        return (
        ('choice1', 'This is the choice 1'),
        ('choice2', 'This is the choice 2'))

# columns
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=128, required=True, translate=True, select=True, track_visibility='onchange'),
        'notes': fields.text('Notes'),
        'integer': fields.integer('integer'),
        'date': fields.date('Date', select=True, track_visibility='onchange'),
        'datetime': fields.datetime('Date Time', select=True, track_visibility='onchange'),
        'image': fields.binary('Files', help='test'),

        'type': fields.selection(XXX_AVAILABLE_TYPES, 'Type', required=True, track_visibility='onchange'),
        'name': fields.selection(_your_selection_function, 'Choice',
                                 help="text"),

        'name': fields.function(_your_field_function, type='char', string='Function'),
        'name': fields.related('relation_field', 'field_name', string='name', type='type', relation='model'),

        'name': fields.many2one('object', 'field_name', required=True, select=True),
        'name': fields.one2many('other.object', 'field_relation_id', 'Field Name', domain=[]),
        'm2m': fields.many2many('other.object.name', id1='field_relation_id', id2='field_name', string='Tags'),

        # Standard fields redefinition
        'partner_id': fields.many2one('res.partner', 'Contact', required=True, select=True),

        # Validity period
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True),
        'active': fields.boolean('Active', readonly=True),
    }

    _rec_name = 'name'

    _order = "name"

    _defaults = {
        'type': XXX_AVAILABLE_TYPES[0],
        'date': fields.date.today,
        'datetime': fields.datetime.now,
        'active': True
    }

# constraints

    def _check_xxx(self, cr, uid, ids, context=None):
        """
        =============
        _check_xxx
        =============
        :rparam: False if ...
                 Else True
        :rtype: Boolean
        """
        return True

    _constraints = [
        (_check_xxx, _('Error! XYZ...'), ['zzz_id']),
    ]

    _sql_constraints = [
        # only if all columns must be non null
        ('col1_col2_..._unique', 'unique (col1,col2, ...)', 'The couple (column desc 2, ...) must be unique for a given column desc 1 !')
    ]

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            display_name = record.name
            res.append((record['id'], display_name))
        return res

    def create(self, cr, uid, vals, context=None):
        res = super(xxxx, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(xxxx, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(xxxx, self).unlink(cr, uid, ids, context=context)
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        res = super(xxxx, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default.update({
                        'active': True,
                        'expire_date': False,

                        'm2m': [],
                       })
        res = super(xxxx, self).copy(cr, uid, ids, default=default, context=context)
        return res

# view methods: onchange, button

    def button_zzz(self, cr, uid, ids, context=None):
        """
        ==========
        button_zzz
        ==========
        This method ...
        :rparam: True
        :rtype: boolean
        :raise: Error if the coordinate is main
                and another coordinate of the same type exists
        """
        return True

# workflow

# public methods

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
