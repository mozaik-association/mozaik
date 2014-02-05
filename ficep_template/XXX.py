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
from openerp.tools.translate import _


class xxxx(orm.Model):

    def _your_field_function(self):
        pass

    def _your_selection_function(self):
        return (
        ('choice1', 'This is the choice 1'),
        ('choice2', 'This is the choice 2'))

    _name = 'XXXXX'
    _rec_name = 'name'
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'name': fields.function(_your_field_function, type='char', string='Name'),
        'date': fields.date('Date', select=1),
        'name': fields.many2one('object', 'field_name'),
        'name': fields.one2many('other.object', 'field_relation_id', 'Field Name'),
        'name': fields.char('name', size=64, select=1),
        'name': fields.selection(_your_selection_function, 'Choose',
            help="text"),
        'name': fields.text('Notes'),
        'name': fields.many2many('other.object.name', id1='field_relation_id', id2='field_name', string='Tags'),
        'name': fields.boolean('Active'),
        'name': fields.related('field_name', type='type', relation='model', string='name'),
        'image': fields.binary("Files", help="test"),
        'name': fields.integer('integer'),
        }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        return super(xxxx, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        return super(xxxx, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return super(xxxx, self).unlink(cr, uid, ids, context=context)

    def copy(self, cr, uid, ids, default=None, context=None):
        if context is None:
            context = {}
        return super(xxxx, self).copy(cr, uid, id, default=default, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
