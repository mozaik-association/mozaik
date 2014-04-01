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

QQQ_AVAILABLE_STATES = [
    ('draft', 'Unconfirmed'),
    ('confirm', 'Confirmed'),
    ('cancel', 'Cancelled'),
]

qqq_available_states = dict(QQQ_AVAILABLE_STATES)


class res_partner_title(orm.Model):
    _inherit = 'res.partner.title'

    def create(self, cr, uid, vals, context=None):
        res = super(res_partner_title, self).create(cr, uid, vals, context=context)
        return res

class res_partner(orm.Model):

    _inherit = 'res.partner'

class xxxx(orm.Model):

    _name = 'xxx'
    _description = 'XXX'
    _inherit = ['abstract.ficep.model']

# private methods

    def _your_method(self, cr, uid, ids, context=None):
         _, xml_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'model', 'xmlid')
         return xml_id
     
    def _your_field_function(self):
        pass

    def _your_selection_function(self):
        return (
        ('choice1', 'This is the choice 1'),
        ('choice2', 'This is the choice 2'))

# data model

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

        'name_id': fields.many2one('other.model', 'field_name', required=True, select=True),
        'name_ids': fields.one2many('other.model', 'field_relation_id', string='Field Name', domain=[]),
        'name_m2m_ids': fields.many2many('other.model', 'cur_model_other_model_rel', id1='cur_model_relation_id', id2='other_model_relation_id', string='Tags'),

        # Standard fields redefinition
        'partner_id': fields.many2one('res.partner', 'Contact', required=True, select=True),
        'hhh': fields.char('HHH', readonly=True, required=True, select=True, track_visibility='onchange',
                           states={'draft': [('readonly', False),('required', False)]}),

        # State
        'state': fields.selection(QQQ_AVAILABLE_STATES,'Status', required=True, track_visibility='onchange',
            help='If qqq is created, the status is \'Unconfirmed\'. If qqq is confirmed the status is set to \'Confirmed\'. Finally, if event is cancelled the status is set to \'Cancelled\'.'),

        # Validity period
        'create_date': fields.datetime('Creation Date'),
        'expire_date': fields.datetime('Expiration Date', track_visibility='onchange'),
        'active': fields.boolean('Active'),

        # parent tree
        'parent_id': fields.many2one('xxx', 'XXX Parent', select=True, track_visibility='onchange'),
        'parent_left': fields.integer('Left Parent', select=True),
        'parent_right': fields.integer('Right Parent', select=True),
    }

    _rec_name = 'name'

    _order = 'name'

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    _defaults = {
        'type': XXX_AVAILABLE_TYPES[0],
        'date': fields.date.today,
        'datetime': fields.datetime.now,
        'active': True,
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
        (orm.Model._check_recursion, _('Error ! You can not create recursive instances'), ['parent_id']),
    ]

    _sql_constraints = [
        # only if all columns must be non null
        ('col1_col2_..._unique', 'unique (col1,col2, ...)', 'The couple (column desc 2, ...) must be unique for a given column desc 1 !')
    ]

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

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

    def copy_data(self, cr, uid, id, default=None, context=None):
        default = dict(default or {})
        default.update({
            'key': 45,
        })
        res = super(xxxx, self).copy_data(cr, uid, id, default=default, context=context)
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

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        res = super(xxxx, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
        return res

    def _read_flat(self, cr, user, ids, fields_to_read, context=None, load='_classic_read'):
        res = super(xxxx, self)._read_flat(cr, user, ids, fields_to_read, context=context, load=load)
        return res

    def browse(self, cr, uid, select, context=None, list_class=None, fields_process=None):
        res = super(xxxx, self).browse(cr, uid, select, context=context, list_class=list_class, fields_process=fields_process)
        return res
    
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(xxxx, self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res

    def fields_get(self, cr, user, allfields=None, context=None, write_access=True):
        res = super(xxxx, self).fields_get(cr, user, allfields=allfields, context=context, write_access=write_access)
        return res

    def _disable_workflow_buttons(self, cr, uid, node):
        arch = super(xxxx,self)._disable_workflow_buttons(cr, uid, node)
        if arch.tag == 'form' and arch.xpath("//field[@name='active']"):
            pass
        return arch

# view methods: onchange, button

    def button_zzz(self, cr, uid, ids, context=None):
        """
        ==========
        button_zzz
        ==========
        This method ...
        :rparam: True
        :rtype: boolean
        :raise: Error if ...
        """
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def button_reset(self, cr, uid, ids, context=None):
        """
        ============
        button_reset
        ============
        Resurrect the ...
        :rparam: True
        :rtype: boolean
        """
        self.write(cr, uid, ids, {'state': 'draft', 'active': True, 'expire_date': False}, context=context)
        return True

# workflow

# public methods

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
