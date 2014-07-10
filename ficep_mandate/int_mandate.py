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

from openerp.addons.ficep_mandate.abstract_mandate import abstract_candidature
from openerp.addons.ficep_mandate.mandate import mandate_category

CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('rejected', 'Rejected'),
    ('suggested', 'Suggested'),
    ('elected', 'Elected'),
]

candidature_available_states = dict(CANDIDATURE_AVAILABLE_STATES)


class int_selection_committee(orm.Model):
    _name = 'int.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    _candidature_model = 'int.candidature'
    _assembly_model = 'int.assembly'
    _assembly_category_model = 'int.assembly.category'
    _mandate_category_foreign_key = 'int_assembly_category_id'
    _form_view = 'int_selection_committee_form_view'
    _parameters_key = 'int_candidature_invalidation_delay'

    def _get_suggested_candidatures(self, cr, uid, ids, context=None):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        return super(int_selection_committee, self)._get_suggested_candidatures(cr, uid, ids, context=context)

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                         required=True, track_visibility='onchange', domain=[('type', '=', 'int')]),
        'is_virtual': fields.boolean('Is Virtual'),
        'assembly_id': fields.many2one(_assembly_model, string='Internal Assembly', track_visibility='onchange',
                                       domain=[('designation_int_assembly_id', '!=', False)]),
        'candidature_ids': fields.one2many(_candidature_model, 'selection_committee_id', 'Internal Candidatures',
                                               domain=[('active', '<=', True)]),
        'assembly_category_id': fields.related('mandate_category_id', _mandate_category_foreign_key, string='Internal Assembly Category',
                                          type='many2one', relation=_assembly_category_model,
                                          store=False),
    }

    _defaults = {
        'is_virtual': True,
    }

    _order = 'assembly_id, mandate_start_date, mandate_category_id, name'

# constraints

    _unicity_keys = 'assembly_id, mandate_start_date, mandate_category_id, name'

# view methods: onchange, button

    def action_copy(self, cr, uid, ids, context=None):
        """
        ==========================
        action_copy
        ==========================
        Duplicate committee and keep rejected internal candidatures
        :rparam: True
        :rtype: boolean
        """
        return super(int_selection_committee, self).action_copy(cr, uid, ids, context=context)

    def button_accept_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_accept_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        return super(int_selection_committee, self).button_accept_candidatures(cr, uid, ids, context=context)

    def button_refuse_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_refuse_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        return super(int_selection_committee, self).button_refuse_candidatures(cr, uid, ids, context=context)

    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        return super(int_selection_committee, self).onchange_assembly_id(cr, uid, ids, assembly_id, context=None)

    def process_invalidate_candidatures_after_delay(self, cr, uid, context=None):
        """
        ===========================================
        process_invalidate_candidatures_after_delay
        ===========================================
        This method is used to invalidate candidatures after a defined elapsed time
        :rparam: True
        :rtype: boolean
        """
        return super(int_selection_committee, self).process_invalidate_candidatures_after_delay(cr, uid, context=context)


class int_candidature(orm.Model):

    _name = 'int.candidature'
    _description = "Internal Candidature"
    _inherit = ['abstract.candidature']

    _mandate_model = 'int.mandate'
    _selection_committee_model = 'int.selection.committee'
    _init_mandate_columns = list(abstract_candidature._init_mandate_columns)
    _init_mandate_columns.extend(['int_assembly_id', 'months_before_end_of_mandate'])
    _allowed_inactive_link_models = [_selection_committee_model]
    _mandate_form_view = 'int_mandate_form_view'
    _unique_id_sequence = 0

    _mandate_category_store_trigger = {
        'int.candidature': (lambda self, cr, uid, ids, context=None: ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('int.candidature').search(cr, uid, [('selection_committee_id', 'in', ids)], context=context),
                                     ['mandate_category_id'], 20),
    }

    _int_assembly_store_trigger = {
        'int.candidature': (lambda self, cr, uid, ids, context=None: ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('int.candidature').search(cr, uid, [('selection_committee_id', 'in', ids)], context=context),
                                     ['int_assembly_id'], 20),
    }

    _designation_assembly_store_trigger = {
        'int.candidature': (lambda self, cr, uid, ids, context=None: ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('int.candidature').search(cr, uid, [('selection_committee_id', 'in', ids)], context=context),
                                     ['designation_int_assembly_id'], 20),
    }

    _mandate_start_date_store_trigger = {
        'int.candidature': (lambda self, cr, uid, ids, context=None: ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('int.candidature').search(cr, uid, [('selection_committee_id', 'in', ids)], context=context),
                                     ['mandate_start_date'], 20),
    }

    _columns = {
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'selection_committee_id': fields.many2one(_selection_committee_model, string='Selection Committee',
                                                 required=True, select=True, track_visibility='onchange'),
        'mandate_category_id': fields.related('selection_committee_id', 'mandate_category_id', string='Mandate Category',
                                          type='many2one', relation="mandate.category",
                                          store=_mandate_category_store_trigger, domain=[('type', '=', 'int')]),
        'mandate_start_date': fields.related('selection_committee_id', 'mandate_start_date', string='Mandate Start Date',
                                          type='date', store=_mandate_start_date_store_trigger),
        'int_assembly_id': fields.related('selection_committee_id', 'assembly_id', string='Internal Assembly',
                                          type='many2one', relation="int.assembly",
                                          store=_int_assembly_store_trigger),
        'designation_int_assembly_id': fields.related('selection_committee_id', 'designation_int_assembly_id', string='Designation Assembly',
                                          type='many2one', relation="int.assembly",
                                          store=_designation_assembly_store_trigger),
        'months_before_end_of_mandate': fields.related('int_assembly_id', 'months_before_end_of_mandate', string='Alert Delay (#Months)',
                                          type='integer', relation="int.assembly",
                                          store=False),
        'mandate_ids': fields.one2many(_mandate_model, 'candidature_id', 'Internal Mandates',
                                       domain=[('active', '<=', True)]),
    }

    _order = 'int_assembly_id, mandate_start_date, mandate_category_id, partner_name'

# view methods: onchange, button

    def onchange_selection_committee_id(self, cr, uid, ids, selection_committee_id, context=None):
        res = {}
        selection_committee = self.pool.get(self._selection_committee_model).browse(cr, uid, selection_committee_id, context)

        res['value'] = dict(int_assembly_id=selection_committee.assembly_id.id or False,
                            designation_int_assembly_id=selection_committee.designation_int_assembly_id.id or False,
                            mandate_category_id=selection_committee.mandate_category_id.id or False,)
        return res

    def button_create_mandate(self, cr, uid, ids, context=None):
        return super(int_candidature, self).button_create_mandate(cr, uid, ids, context=context)


class int_mandate(orm.Model):

    _name = 'int.mandate'
    _description = "Internal Mandate"
    _inherit = ['abstract.mandate']

    _allowed_inactive_link_models = ['int.candidature']
    _undo_redirect_action = 'ficep_mandate.int_mandate_action'
    _unique_id_sequence = 0

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange', domain=[('type', '=', 'int')]),
        'int_assembly_id': fields.many2one('int.assembly', 'Internal Assembly',
                                           domain=[('designation_int_assembly_id', '!=', False)]),
        'int_assembly_category_id': fields.related('mandate_category_id', 'int_assembly_category_id', string='Internal Assembly Category',
                                          type='many2one', relation="int.assembly.category",
                                          store=False),
        'candidature_id': fields.many2one('int.candidature', 'Candidature'),
        'is_submission_mandate': fields.related('mandate_category_id', 'is_submission_mandate', string='Submission to a Mandate Declaration',
                                          type='boolean',
                                          store={'mandate.category': (mandate_category.get_linked_int_mandate_ids, ['is_submission_mandate'], 20)}),
        'is_submission_assets': fields.related('mandate_category_id', 'is_submission_assets', string='Submission to an Assets Declaration',
                                          type='boolean',
                                          store={'mandate.category': (mandate_category.get_linked_int_mandate_ids, ['is_submission_assets'], 20)}),
        'months_before_end_of_mandate': fields.integer('Alert Delay (#Months)', track_visibility='onchange'),
    }

    _order = 'partner_id, int_assembly_id, start_date, mandate_category_id'

# constraints

    _unicity_keys = 'partner_id, int_assembly_id, start_date, mandate_category_id'

# view methods: onchange, button

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_invalidate
        =================
        Invalidates an object
        :rparam: True
        :rtype: boolean
        Note: Argument vals must be the last in the signature
        """
        return super(int_mandate, self).action_invalidate(cr, uid, ids, context=context, vals=vals)

    def action_finish(self, cr, uid, ids, context=None):
        """
        =================
        action_finish
        =================
        Finish mandate at the current date
        :rparam: True
        :rtype: boolean
        """
        return super(int_mandate, self).action_finish(cr, uid, ids, context=context)

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        int_assembly_category_id = False

        if mandate_category_id:
            category_data = self.pool.get('mandate.category').read(cr, uid, mandate_category_id, ['int_assembly_category_id'], context)
            int_assembly_category_id = category_data['int_assembly_category_id'] or False

        res = {
            'int_assembly_category_id': int_assembly_category_id,
            'int_assembly_id': False,
        }
        return {
            'value': res,
        }

    def onchange_int_assembly_id(self, cr, uid, ids, ext_assembly_id, context=None):
        res = {}
        res['value'] = dict(months_before_end_of_mandate=False, designation_int_assembly_id=False)
        if ext_assembly_id:
            assembly = self.pool.get('int.assembly').browse(cr, uid, ext_assembly_id)

            res['value'] = dict(months_before_end_of_mandate=assembly.months_before_end_of_mandate,
                                designation_int_assembly_id=assembly.designation_int_assembly_id.id)

        return res
