# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('rejected', 'Rejected'),
    ('suggested', 'Suggested'),
    ('elected', 'Elected'),
]

candidature_available_states = dict(CANDIDATURE_AVAILABLE_STATES)



class ExtCandidature(models.Model):
    _name = 'ext.candidature'
    _description = "External Candidature"
    _inherit = ['abstract.candidature']

    _mandate_model = 'ext.mandate'
    _selection_committee_model = 'ext.selection.committee'
    _init_mandate_columns = list(abstract_candidature._init_mandate_columns)
    _init_mandate_columns.extend(['ext_assembly_id',
                                  'months_before_end_of_mandate'])
    _allowed_inactive_link_models = [_selection_committee_model]
    _mandate_form_view = 'ext_mandate_form_view'
    _unique_id_sequence = 400000000

    _mandate_category_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['mandate_category_id'], 20),
    }

    _ext_assembly_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['ext_assembly_id'], 20),
    }

    _designation_assembly_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['designation_int_assembly_id'], 20),
    }

    _mandate_start_date_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['mandate_start_date'], 20),
    }

    _columns = {
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES,
                                  'Status',
                                  readonly=True,
                                  track_visibility='onchange', ),
        'selection_committee_id': fields.many2one(_selection_committee_model,
                                                  string='Selection Committee',
                                                  required=True,
                                                  select=True,
                                                  track_visibility='onchange'),
        'mandate_category_id': fields.related(
            'selection_committee_id',
            'mandate_category_id',
            string='Mandate Category',
            type='many2one',
            relation="mandate.category",
            store=_mandate_category_store_trigger,
            domain=[('type', '=', 'ext')]),
        'mandate_start_date': fields.related(
            'selection_committee_id',
            'mandate_start_date',
            string='Mandate Start Date',
            type='date',
            store=_mandate_start_date_store_trigger),
        'ext_assembly_id': fields.related('selection_committee_id',
                                          'assembly_id',
                                          string='External Assembly',
                                          type='many2one',
                                          relation="ext.assembly",
                                          store=_ext_assembly_store_trigger),
        'designation_int_assembly_id': fields.related(
            'selection_committee_id',
            'designation_int_assembly_id',
            string='Designation Assembly',
            type='many2one',
            relation="int.assembly",
            store=_designation_assembly_store_trigger),
        'months_before_end_of_mandate': fields.related(
            'ext_assembly_id',
            'months_before_end_of_mandate',
            string='Alert Delay (#Months)',
            type='integer',
            relation="ext.assembly",
            store=False),
        'mandate_ids': fields.one2many(_mandate_model,
                                       'candidature_id',
                                       'External Mandates',
                                       domain=[('active', '<=', True)]),
    }

    _order = 'ext_assembly_id, mandate_start_date, mandate_category_id, \
                  partner_name'

    # view methods: onchange, button

    def onchange_selection_committee_id(self, cr, uid, ids,
                                        selection_committee_id, context=None):
        res = {}
        selection_committee = self.pool.get(
            self._selection_committee_model).browse(
            cr,
            uid,
            selection_committee_id,
            context)
        assembly = selection_committee.designation_int_assembly_id.id
        res['value'] = dict(
            ext_assembly_id=selection_committee.assembly_id.id,
            designation_int_assembly_id=assembly,
            mandate_category_id=selection_committee.mandate_category_id.id)
        return res

    def button_create_mandate(self, cr, uid, ids, context=None):
        return super(ext_candidature,
                     self).button_create_mandate(cr, uid, ids, context=context)

