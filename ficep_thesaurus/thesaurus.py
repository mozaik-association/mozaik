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
    _inherit = ['abstract.ficep.model']
    _description = 'Thesaurus'

    _track = {
        'new_thesaurus_term_id': {
            'ficep_thesaurus.mt_thesaurus_add_term': lambda self, cr, uid, obj, ctx=None: obj.new_thesaurus_term_id,
        },
    }

    _columns = {
        'name': fields.char('Thesaurus', size=50, required=True, track_visibility='onchange'),
        'new_thesaurus_term_id': fields.many2one('thesaurus.term', string='New Term to Validate', readonly=True, track_visibility='onchange'),
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

# public methods

    def update_notification_term(self, cr, uid, ids, newid=False, context=None):
        """
        ========================
        update_notification_term
        ========================
        Update the field new_thesaurus_term_id producing or not a notification
        """
        ctx = context
        if not newid:
            # context: notrack when resetting the new term id to False to avoid a notification
            ctx = dict(context or {}, mail_notrack=True)
        res = self.write(cr, uid, ids, {'new_thesaurus_term_id': newid}, context=ctx)
        return res


class thesaurus_term(orm.Model):

    _name = 'thesaurus.term'
    _inherit = ['abstract.ficep.model']
    _description = 'Thesaurus Term'

    def _get_technical_name(self, cr, uid, ids, name, args, context=None):
        result = {}.fromkeys(ids, False)
        terms = self.browse(cr, uid, ids, context=context)
        for term in terms:
            elts = [
                '%s' % term.thesaurus_id.id,
                term.state,
                term.state == 'draft' and term.name or term.state == 'confirm' and term.ext_identifier or term.expire_date
            ]
            result[term.id] = '#'.join([el for el in elts if el])

        return result

    _columns = {
        'name': fields.char('Term', required=True, select=True, track_visibility='onchange'),
        'thesaurus_id': fields.many2one('thesaurus', 'Thesaurus', readonly=True, required=True),
        'ext_identifier': fields.char('External Identifier', required=False, select=True, track_visibility='onchange',
                                      states={'confirm': [('required', True)]}),
        'technical_name': fields.function(_get_technical_name, string='Technical Name', type='char', select=True, required=True,
                                          store=True),

        # State
        'state': fields.selection(TERM_AVAILABLE_STATES, 'Status', readonly=True, required=True, track_visibility='onchange',
            help='If term is created, the status is \'Unconfirmed\'.If term is confirmed the status is set to \'Confirmed\'. If event is cancelled the status is set to \'Cancelled\'.'),
    }

    _order = 'name'

    _defaults = {
        'thesaurus_id': lambda self, cr, uid, ids, context=None: self.pool['thesaurus'].search(cr, uid, [], limit=1, context=context)[0],
        'ext_identifier': False,
        'state': TERM_AVAILABLE_STATES[1][0],
        'technical_name': '#',
    }

# constraints

    def _check_ext_identifier(self, cr, uid, ids, context=None):
        """
        =====================
        _check_ext_identifier
        =====================
        Check if ext_identifier is known when validating term
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        terms = self.browse(cr, uid, ids, context=context)
        for term in terms:
            if term.state == 'confirm' and term.ext_identifier == False:
                return False

        return True

    _constraints = [
        (_check_ext_identifier, _('Missing External Identifier for a validated term'),
          ['state', 'ext_identifier'])
    ]

    _sql_constraints = [
        ('check_unicity_technical_name', 'unique(technical_name)', _('The term must be unique in the thesaurus!'))
    ]

# orm methods

    def load(self, cr, uid, fields, data, context=None):
        """
        Do not add messages when importing terms
        """
        ctx = context or {}
        ctx.update({
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'mail_notrack': True,
        })
        if 'id' not in fields:
            fields.append('id')
            j = 0
            if len(fields) > 1 and fields[1] == 'ext_identifier':
                j = 1
            for i in range(len(data)):
                data[i] += ('__IMP_THT_%s' % data[i][j],)
        res = super(thesaurus_term, self).load(cr, uid, fields, data, context=ctx)
        return res

    def create(self, cr, uid, vals, context=None):
        """
        Create a new term and notify it to the thesaurus to send a message to the followers.
        :param: vals
        :type: dictionary that contains at least 'name'
        :rparam: id of the new term
        :rtype: integer
        """
        new_id = super(thesaurus_term, self).create(cr, uid, vals, context=context)
        if context and 'default_state' in context:
            term = self.browse(cr, uid, new_id, context=context)
            # Reset notification term on the thesaurus
            self.pool['thesaurus'].update_notification_term(cr, uid, term.thesaurus_id.id, context=None)
            # Set notification term on the thesaurus
            self.pool['thesaurus'].update_notification_term(cr, uid, term.thesaurus_id.id, new_id, context=None)
        return new_id

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Reset some fields to their initial values.
        Mark the name as (copy)
        """
        default = default or {}
        default.update({
            'ext_identifier': False,
            'state': TERM_AVAILABLE_STATES[0][0],
            'technical_name': '#',
        })
        res = super(thesaurus_term, self).copy_data(cr, uid, ids, default=default, context=context)
        res.update({
            'name': _('%s (copy)') % res.get('name'),
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
        self.write(cr, uid, ids, {'state': TERM_AVAILABLE_STATES[1][0]}, context=context)
        return True

    def button_cancel(self, cr, uid, ids, context=None):
        """
        =============
        button_cancel
        =============
        Cancel the term
        :rparam: True
        :rtype: boolean
        Note:
        Reset the notification term to avoid the expected exception related to an active reference
        """
        term = self.browse(cr, uid, ids, context=context)[0]
        # Reset notification term on the thesaurus
        self.pool['thesaurus'].update_notification_term(cr, uid, term.thesaurus_id.id, context=None)
        res = super(thesaurus_term, self).action_invalidate(cr, uid, ids, vals={'state': TERM_AVAILABLE_STATES[2][0]}, context=context)
        return res

    def button_reset(self, cr, uid, ids, context=None):
        """
        ============
        button_reset
        ============
        Cancel the term
        :rparam: True
        :rtype: boolean
        """
        res = super(thesaurus_term, self).action_validate(cr, uid, ids, vals={'state': TERM_AVAILABLE_STATES[0][0]}, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
