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
from openerp.tools.translate import _


"""
Available States for thesaurus terms
"""
TERM_AVAILABLE_STATES = [
    ('draft', 'Unconfirmed'),
    ('confirm', 'Confirmed'),
    ('cancel', 'Cancelled'),
]

term_available_states = dict(TERM_AVAILABLE_STATES)


class thesaurus(orm.Model):

    _name = 'thesaurus'
    _description = 'Thesaurus'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _track = {
        'new_thesaurus_term_id': {
            'ficep_thesaurus.mt_thesaurus_add_term': lambda self, cr, uid, obj, ctx=None: obj.new_thesaurus_term_id,
        },
    }

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Thesaurus', size=50, required=True, track_visibility='onchange'),
        'new_thesaurus_term_id': fields.many2one('thesaurus.term', string='New Term to Validate', readonly=True, track_visibility='onchange'),

        # Validity
        'active': fields.boolean('Active', readonly=True),
    }

    _defaults = {
        'active': True,
    }

    _order = 'name'

# orm methods

    def copy(self, cr, uid, ids, default=None, context=None):
        """
        ====
        copy
        ====
        Prevent to duplicate a thesaurus
        """
        raise orm.except_orm(_('Error'), _('A thesaurus cannot be duplicated!'))

# view methods: onchange, button

    def button_invalidate(self, cr, uid, ids, context=None):
        """
        =================
        button_invalidate
        =================
        Invalidate the thesaurus
        :rparam: True
        :rtype: boolean
        """
        term_ids = self.pool['thesaurus.term'].search(cr, uid, [('thesaurus_id', 'in', ids)], limit=1, context=context)
        if term_ids:
            raise orm.except_orm(_('Error'), _('A thesaurus with active terms cannot be invalidated!'))
        self.write(cr, uid, ids, {'active': False}, context=context)
        return True

class thesaurus_term(orm.Model):

    _name = 'thesaurus.term'
    _description = 'Thesaurus Term'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Term', required=True, translate=True, select=True, track_visibility='onchange'),
        'ext_id': fields.char('External Identifier', readonly=True, required=False, select=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)], 'confirm': [('required', True)]}),
        'thesaurus_id': fields.many2one('thesaurus', 'Thesaurus', readonly=True, required=True),

        # State
        'state': fields.selection(TERM_AVAILABLE_STATES,'Status', readonly=True, required=True, track_visibility='onchange',
            help='If term is created, the status is \'Unconfirmed\'.If term is confirmed the status is set to \'Confirmed\'. If event is cancelled the status is set to \'Cancelled\'.'),

        # Validity period
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', track_visibility='onchange'),
        'active': fields.boolean('Active', readonly=True),
    }

    _order = 'name'

    _defaults = {
        'state': TERM_AVAILABLE_STATES[0][0],
        'thesaurus_id': lambda self, cr, uid, ids, context=None: self.pool['thesaurus'].search(cr, uid, [], limit=1, context=context)[0],
        'active': True,
    }

    _sql_constraints = [
        ('check_unicity_number', 'unique(thesaurus_id, name)', _('The term must be unique in the thesaurus!'))
    ]

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        Create a new term and notify it to the thesaurus to send a message to the followers.
        :param: vals
        :type: dictionary that contains at least 'name'
        :rparam: id of the new term
        :rtype: integer
        """
        new_id = super(thesaurus_term, self).create(cr, uid, vals, context=context)
        term = self.browse(cr, uid, new_id, context=context)

        # context: notrack when resetting the new term id to False
        reset_context = dict(context or {}, mail_notrack=True)
        self.pool['thesaurus'].write(cr, uid, term.thesaurus_id.id, {'new_thesaurus_term_id': False}, context=reset_context)
        # Send a "New Term to Validate" notification to followers 
        self.pool['thesaurus'].write(cr, uid, term.thesaurus_id.id, {'new_thesaurus_term_id': new_id}, context=context)
        return new_id

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Reset some fields to their initial values.
        Mark the name as (copy) 
        """
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        res.update({
                    'name': _('%s (copy)') % default.get('name'),
                    'active': True,
                    'expire_date': False,
                   })
        return res

# view methods: onchange, button

    def button_confirm(self, cr, uid, ids, context=None):
        """
        ==============
        button_confirm
        ==============
        Confirm the term
        :rparam: True
        :rtype: boolean
        """
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def button_cancel(self, cr, uid, ids, context=None):
        """
        =============
        button_cancel
        =============
        Cancel the term
        Overriding method to kill relation with these expired terms
        :rparam: True
        :rtype: boolean
        """
        self.write(cr, uid, ids, {'state': 'cancel', 'active': False, 'expire_date': fields.datetime.now}, context=context)
        return True

    def button_reset(self, cr, uid, ids, context=None):
        """
        ============
        button_reset
        ============
        Cancel the term
        :rparam: True
        :rtype: boolean
        """
        self.write(cr, uid, ids, {'state': 'draft', 'active': True, 'expire_date': False}, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
