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


class ext_selection_committee(orm.Model):
    _name = 'ext.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    _candidature_model = 'ext.candidature'
    _assembly_model = 'ext.assembly'
    _assembly_category_model = 'ext.assembly.category'
    _mandate_category_foreign_key = 'ext_assembly_category_id'
    _form_view = 'ext_selection_committee_form_view'

    def _get_suggested_candidatures(self, cr, uid, ids, context=None):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        return super(ext_selection_committee, self)._get_suggested_candidatures(cr, uid, ids, context=context)

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                         required=True, track_visibility='onchange', domain=[('type', '=', 'ext')]),
        'is_virtual': fields.boolean('Is Virtual'),
        'assembly_id': fields.many2one(_assembly_model, string='External Assembly', track_visibility='onchange'),
        'candidature_ids': fields.one2many(_candidature_model, 'selection_committee_id', 'External Candidatures',
                                               domain=[('active', '<=', True)]),
        'assembly_category_id': fields.related('mandate_category_id', _mandate_category_foreign_key, string='External Assembly Category',
                                          type='many2one', relation=_assembly_category_model,
                                          store=False),
    }

    _defaults = {
        'is_virtual': False,
    }

    # view methods: onchange, button
    def action_copy(self, cr, uid, ids, context=None):
        """
        ==========================
        action_copy
        ==========================
        Duplicate committee and keep rejected external candidatures
        :rparam: True
        :rtype: boolean
        """
        return super(ext_selection_committee, self).action_copy(cr, uid, ids, context=context)

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
        return super(ext_selection_committee, self).button_accept_candidatures(cr, uid, ids, context=context)

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
        return super(ext_selection_committee, self).button_refuse_candidatures(cr, uid, ids, context=context)

# constraints

    _unicity_keys = 'N/A'

    # view methods: onchange, button
    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        return super(ext_selection_committee, self).onchange_assembly_id(cr, uid, ids, assembly_id, context=None)


class ext_candidature(orm.Model):

    _name = 'ext.candidature'
    _description = "External Candidature"
    _inherit = ['abstract.candidature']

    _mandate_model = 'ext.mandate'
    _selection_committee_model = 'ext.selection.committee'
    _init_mandate_columns = list(abstract_candidature._init_mandate_columns)
    _init_mandate_columns.extend(['ext_assembly_id', 'months_before_end_of_mandate'])
    _allowed_inactive_link_models = [_selection_committee_model]

    _columns = {
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'selection_committee_id': fields.many2one(_selection_committee_model, string='Selection Committee',
                                                 required=True, select=True, track_visibility='onchange'),
        'mandate_category_id': fields.related('selection_committee_id', 'mandate_category_id', string='Mandate Category',
                                          type='many2one', relation="mandate.category",
                                          store=True, domain=[('type', '=', 'ext')]),
        'ext_assembly_id': fields.related('selection_committee_id', 'assembly_id', string='External Assembly',
                                          type='many2one', relation="ext.assembly",
                                          store=True),
         'months_before_end_of_mandate': fields.related('ext_assembly_id', 'months_before_end_of_mandate', string='Months before end of Mandate',
                                          type='integer', relation="ext.assembly",
                                          store=False),
    }

    _order = 'selection_committee_id'

    # view methods: onchange, button
    def onchange_selection_committee_id(self, cr, uid, ids, selection_committee_id, context=None):
        res = {}
        selection_committee = self.pool.get(self._selection_committee_model).browse(cr, uid, selection_committee_id, context)

        res['value'] = dict(ext_assembly_id=selection_committee.assembly_id.id or False,
                            designation_int_assembly_id=selection_committee.designation_int_assembly_id.id or False,
                            mandate_category_id=selection_committee.mandate_category_id.id or False,)
        return res


class ext_mandate(orm.Model):

    _name = 'ext.mandate'
    _description = "External Mandate"
    _inherit = ['abstract.mandate']

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange', domain=[('type', '=', 'ext')]),
        'ext_assembly_id': fields.many2one('ext.assembly', 'External Assembly'),
        'ext_assembly_category_id': fields.related('mandate_category_id', 'ext_assembly_category_id', string='External Assembly Category',
                                          type='many2one', relation="ext.assembly.category",
                                          store=False),
        'candidature_id': fields.many2one('ext.candidature', 'Candidature'),
        'is_submission_mandate': fields.related('mandate_category_id', 'is_submission_mandate', string='Submission to a Mandate Declaration',
                                          type='boolean',
                                          store={'mandate.category': (mandate_category.get_linked_ext_mandate_ids, ['is_submission_mandate'], 20)}),
        'is_submission_assets': fields.related('mandate_category_id', 'is_submission_assets', string='Submission to an Assets Declaration',
                                          type='boolean',
                                          store={'mandate.category': (mandate_category.get_linked_ext_mandate_ids, ['is_submission_assets'], 20)}),
        'competencies_m2m_ids': fields.many2many('thesaurus.term', 'sta_mandate_term_competencies_rel', id1='sta_mandate_id', id2='thesaurus_term_id', string='Competencies'),
        'months_before_end_of_mandate': fields.integer('Months before end of Mandate', track_visibility='onchange'),
    }

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
        return super(ext_mandate, self).action_invalidate(cr, uid, ids, context=context, vals=vals)

    def action_finish(self, cr, uid, ids, context=None):
        """
        =================
        action_finish
        =================
        Finish mandate at the current date
        :rparam: True
        :rtype: boolean
        """
        return super(ext_mandate, self).action_finish(cr, uid, ids, context=context)

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        ext_assembly_category_id = False

        if mandate_category_id:
            category_data = self.pool.get('mandate.category').read(cr, uid, mandate_category_id, ['ext_assembly_category_id'], context)
            ext_assembly_category_id = category_data['ext_assembly_category_id'] or False

        res = {
            'ext_assembly_category_id': ext_assembly_category_id,
            'ext_assembly_id': False,
        }
        return {
            'value': res,
        }

    def onchange_ext_assembly_id(self, cr, uid, ids, ext_assembly_id, context=None):
        res = {}
        res['value'] = dict(months_before_end_of_mandate=False)
        if ext_assembly_id:
            assembly = self.pool.get('ext.assembly').browse(cr, uid, ext_assembly_id)

            res['value'] = dict(months_before_end_of_mandate=assembly.months_before_end_of_mandate)

        return res
