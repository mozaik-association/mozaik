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
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT,\
                          DEFAULT_SERVER_DATE_FORMAT
from openerp.osv import orm, osv, fields
from openerp.tools.translate import _

from openerp.addons.mozaik_mandate.mandate import mandate_category

SELECTION_COMMITTEE_AVAILABLE_STATES = [
    ('draft', 'In Progress'),
    ('done', 'Closed'),
]
selection_committee_available_states = dict(
                                        SELECTION_COMMITTEE_AVAILABLE_STATES)

CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('rejected', 'Rejected'),
    ('suggested', 'Suggested'),
    ('designated', 'Designated'),
    ('elected', 'Elected'),
    ('non-elected', 'Non-Elected'),
]

candidature_available_states = dict(CANDIDATURE_AVAILABLE_STATES)


class abstract_selection_committee(orm.AbstractModel):
    _name = 'abstract.selection.committee'
    _description = 'Abstract Selection Committee'
    _inherit = ['mozaik.abstract.model']

    _candidature_model = 'abstract.candidature'
    _assembly_model = 'abstract.assembly'
    _assembly_category_model = 'abstract.assembly.category'
    _mandate_category_foreign_key = False
    _form_view = 'abstract_selection_committee_form_view'
    _parameters_key = False

    def _get_suggested_candidatures(self, cr, uid, ids, context=None):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        res = []
        committee = self.browse(cr, uid, ids[0], context=context)
        for candidature in committee.candidature_ids:
            if candidature.state == 'rejected':
                continue
            elif candidature.state == 'suggested':
                res.append(candidature.id)
            else:
                raise osv.except_osv(_('Operation Forbidden!'),
                        _('Some candidatures are still in "declared" state'))
        return res

    _columns = {
        'state': fields.selection(SELECTION_COMMITTEE_AVAILABLE_STATES,
                                  'Status',
                                  readonly=True,
                                  track_visibility='onchange',),
        'mandate_category_id': fields.many2one('mandate.category',
                                               string='Mandate Category',
                                                 required=True,
                                                 track_visibility='onchange'),
        'assembly_id': fields.many2one(_assembly_model,
                                       string='Abstract Assembly',
                                       track_visibility='onchange'),
        'candidature_ids': fields.one2many(_candidature_model,
                                           'selection_committee_id',
                                           'Abstract Candidatures',
                                           domain=[('active', '<=', True)]),
        'assembly_category_id': fields.related(
                                        'mandate_category_id',
                                        _mandate_category_foreign_key,
                                        string='Abstract Assembly Category',
                                        type='many2one',
                                        relation=_assembly_category_model,
                                        store=False),
        'designation_int_assembly_id': fields.many2one(
                                        'int.assembly',
                                        string='Designation Assembly',
                                        required=True,
                                        track_visibility='onchange',
                                        domain=[
                                        ('is_designation_assembly', '=', True)
                                        ]),
        'decision_date': fields.date('Designation Date',
                                     track_visibility='onchange'),
        'mandate_start_date': fields.date('Mandates Start Date',
                                          required=True,
                                          track_visibility='onchange'),
        'mandate_deadline_date': fields.date('Mandates Deadline Date',
                                             required=True,
                                             track_visibility='onchange'),
        'meeting_date': fields.date('Meeting Date',
                                    track_visibility='onchange'),
        'name': fields.char('Name',
                            size=128,
                            select=True,
                            required=True,
                            track_visibility='onchange'),
        'note': fields.text('Notes',
                            track_visibility='onchange'),
        'auto_mandate': fields.boolean("Create Mandates after Election"),
    }

    _defaults = {
        'state': SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
        'auto_mandate': False,
    }

# constraints

    _unicity_keys = 'N/A'

    _sql_constraints = [
        ('date_check', "CHECK(mandate_start_date <= mandate_deadline_date)",
         "The start date must be anterior to the deadline date."),
    ]

    def _check_decision_date(self, cr, uid, ids, context=None):
        """
        ====================
        _check_decision_date
        ====================
        Check if decision_date is not null when accepting the proposal
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """

        committees = self.browse(cr, uid, ids)

        for committee in committees:
            if committee.state == 'done' and not committee.decision_date:
                return False
        return True

    _constraints = [
        (_check_decision_date,
         _('A decision date is mandatory when accepting the proposal '
           'of the committee'), ['state', 'decision_date'])
    ]

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if not context:
            context = self.pool.get('res.users').context_get(cr, uid)

        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for committee in self.browse(cr, uid, ids, context=context):
            display_name = u'{assembly}/{start} ({name})'.format(
                     assembly=committee.assembly_id.name,
                     start=self.pool.get('res.lang').format_date(
                                                 cr,
                                                 uid,
                                                 committee.mandate_start_date,
                                                 context) or False,
                     name=committee.name,)
            res.append((committee['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            assembly_ids = self.pool[self._assembly_model].search(
                                                  cr,
                                                  uid,
                                                  [('name', operator, name)],
                                                  context=context)
            ids = self.search(cr, uid, ['|',
                                        ('name', operator, name),
                                        ('assembly_id', 'in', assembly_ids)]
                                        + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def copy_data(self, cr, uid, id_, default=None, context=None):
        default = default or {}

        default.update({
            'active': True,
            'state': SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
            'note': False,
            'decision_date': False,
            'meeting_date': False,
            'candidature_ids': False,
        })
        res = super(abstract_selection_committee, self).copy_data(
                                                              cr,
                                                              uid,
                                                              id_,
                                                              default=default,
                                                              context=context)

        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res

# view methods: onchange, button

    def action_copy(self, cr, uid, ids, context=None):
        """
        ==========================
        action_copy
        ==========================
        Duplicate committee and keep rejected candidatures
        :rparam: True
        :rtype: boolean
        """
        copied_committee_id = ids[0]
        candidature_pool = self.pool.get(self._candidature_model)
        rejected_candidature_ids = candidature_pool.search(
                       cr,
                       uid,
                       [('selection_committee_id', '=', copied_committee_id),
                        ('state', '=', 'rejected')])
        new_committee_id = self.copy(cr,
                                     uid,
                                     copied_committee_id,
                                     None,
                                     context)
        if rejected_candidature_ids:
            candidature_pool.write(
                               cr,
                               uid,
                               rejected_candidature_ids,
                               {'selection_committee_id': new_committee_id})
            candidature_pool.signal_workflow(cr,
                                             uid,
                                             rejected_candidature_ids,
                                             'button_declare',
                                             context=context)

        return self.display_object_in_form_view(cr, uid, new_committee_id,
                                                context=context)

    def button_accept_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_accept_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id
        in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        for committee in self.browse(cr, uid, ids, context=context):
            if committee.candidature_ids:
                self.pool.get(self._candidature_model).signal_workflow(cr,
                                                                       uid,\
                    self._get_suggested_candidatures(cr,
                                                     uid,
                                                     ids,
                                                     context=context),
                                                    'action_accept',
                                                    context=context)
        self.action_invalidate(cr, uid, ids, context, {'state': 'done'})
        return True

    def button_refuse_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_refuse_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id
        in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        for committee in self.browse(cr, uid, ids, context=context):
            if committee.candidature_ids:
                self.pool.get(self._candidature_model).signal_workflow(
                                   cr,
                                   uid,
                                   self._get_suggested_candidatures(
                                                            cr,
                                                            uid,
                                                            ids,
                                                            context=context),
                                   'button_declare',
                                   context=context)
            self.write(cr, uid, ids, {'decision_date': False}, context=context)
        return True

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id,
                                     context=None):
        res = {}
        assembly_category_id = False
        if mandate_category_id:
            mandate_category = self.pool.get('mandate.category').browse(
                                                        cr,
                                                        uid,
                                                        mandate_category_id,
                                                        context)
            values =\
        dict(
        sta_assembly_category_id=mandate_category.sta_assembly_category_id.id\
                                 or False,
        int_assembly_category_id=mandate_category.int_assembly_category_id.id\
                                 or False,
        ext_assembly_category_id=mandate_category.ext_assembly_category_id.id\
                                 or False,
                                )
            assembly_category_id = values[self._mandate_category_foreign_key]
        res['value'] = dict(assembly_category_id=assembly_category_id)
        return res

    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        res = {}
        res['value'] = dict(assembly_category_id=False,
                            mandate_category_id=False)
        if assembly_id:
            assembly = self.pool.get(self._assembly_model).browse(cr,
                                                                  uid,
                                                                  assembly_id)
            mandate_category_ids = self.pool.get('mandate.category').search(
                                        cr,
                                        uid,
                                        [(self._mandate_category_foreign_key,
                                          '=',
                                          assembly.assembly_category_id.id)])
            mandate_category_id = False
            if mandate_category_ids:
                mandate_category_id = mandate_category_ids[0]

            res['value'] = dict(\
                        assembly_category_id=assembly.assembly_category_id.id\
                                             or False,
                        mandate_category_id=mandate_category_id)

            if self.pool.get(self._assembly_model)._columns.get(
                                                'designation_int_assembly_id'):
                res['value']['designation_int_assembly_id'] =\
                                        assembly.designation_int_assembly_id.id
        return res

# public methods

    def process_invalidate_candidatures_after_delay(self, cr, uid,
                                                    context=None):
        """
        ===========================================
        process_invalidate_candidatures_after_delay
        ===========================================
        This method is used to invalidate candidatures after a defined elapsed
        time
        :rparam: True
        :rtype: boolean
        """
        SQL_QUERY = """
            SELECT DISTINCT committee.id
             FROM %s AS committee
             JOIN %s candidature
               ON candidature.selection_committee_id = committee.id
            WHERE committee.active = False
              AND candidature.active = True
          """
        cr.execute(SQL_QUERY % (self._name.replace('.', '_'),
                                self._candidature_model.replace('.', '_')))
        committee_ids = self.search(cr,
                                    uid,
                                    [('id', 'in',
                                    [committee[0] for committee
                                                      in cr.fetchall()]),
                                     ('active', '=', False)],
                                    context=context)

        invalidation_delay = int(
                self.pool.get('ir.config_parameter').get_param(
                                                        cr,
                                                        uid,
                                                        self._parameters_key,
                                                        60))

        for committee in self.browse(cr, uid, committee_ids, context=context):
            limit_date = datetime.strptime(
                              committee.expire_date,
                              DEFAULT_SERVER_DATETIME_FORMAT)\
                              + relativedelta(days=invalidation_delay or 0.0)
            if datetime.strptime(fields.datetime.now(),
                                 DEFAULT_SERVER_DATETIME_FORMAT) >= limit_date:
                self.pool.get(
                        self._candidature_model).action_invalidate(
                                                cr,
                                                uid,
                                                [candidature.id
                                                 for candidature in
                                                 committee.candidature_ids],
                                                context=context)

        return True


class abstract_mandate(orm.AbstractModel):

    _name = 'abstract.mandate'
    _description = 'Abstract Mandate'
    _inherit = ['abstract.duplicate']

    _inactive_cascade = True
    _discriminant_field = 'partner_id'
    _discriminant_model = 'generic.mandate'
    _trigger_fields = ['mandate_category_id',
                       'partner_id',
                       'start_date',
                       'deadline_date']

    _unique_id_store_trigger = {
    }

    def _compute_unique_id(self, cr, uid, ids, fname, arg, context=None):
        res = {}
        for retro_id in ids:
            res[retro_id] = retro_id + self._unique_id_sequence

        return res

    _columns = {
        'unique_id': fields.function(_compute_unique_id,
                                     type="integer",
                                     string="Unique id",
                                     store=_unique_id_store_trigger),
        'partner_id': fields.many2one('res.partner',
                                      'Representative',
                                      required=True,
                                      select=True,
                                      track_visibility='onchange'),
        'mandate_category_id': fields.many2one('mandate.category',
                                               string='Mandate Category',
                                               required=True,
                                               select=True,
                                               track_visibility='onchange'),
        'designation_int_assembly_id': fields.many2one(
                                                'int.assembly',
                                                'Designation Assembly',
                                                required=True,
                                                select=True,
                                                track_visibility='onchange',
                                                domain=[
                                                    ('is_designation_assembly',
                                                     '=', True)]),
        'start_date': fields.date('Start Date',
                                  required=True,
                                  track_visibility='onchange'),
        'deadline_date': fields.date('Deadline Date',
                                     required=True,
                                     track_visibility='onchange'),
        'end_date': fields.date('End Date',
                                track_visibility='onchange'),
        'is_submission_mandate': fields.related(
                                'mandate_category_id',
                                'is_submission_mandate',
                                string='Submission to a Mandate Declaration',
                                type='boolean',
                                store=True),
        'is_submission_assets': fields.related(
                                'mandate_category_id',
                                'is_submission_assets',
                                string='Submission to an Assets Declaration',
                                type='boolean',
                                store=True),
        'candidature_id': fields.many2one('abstract.candidature',
                                          'Candidature'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate',
                                               track_visibility='onchange'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate',
                                                track_visibility='onchange'),
        'alert_date': fields.date('Alert Date'),
        # Duplicates: redefine string
        'is_duplicate_detected': fields.boolean('Incompatible Mandate',
                                                readonly=True),
        'is_duplicate_allowed': fields.boolean('Allowed Incompatible Mandate',
                                               readonly=True,
                                               track_visibility='onchange'),
    }

    _defaults = {
        'end_date': False,
    }

# constraints

    _unicity_keys = 'N/A'

    _sql_constraints = [
        ('date_check', "CHECK(start_date <= deadline_date)",
         "The start date must be anterior to the deadline date."),
        ('date_check2',
         "CHECK((end_date = NULL) or ((start_date <= end_date) and \
         (end_date <= deadline_date)))",
         "The end date must be between start date and deadline date."),
    ]

# view methods: onchange, button

    def action_finish(self, cr, uid, ids, context=None):
        """
        =================
        action_finish
        =================
        Finish mandate at the current date
        :rparam: True
        :rtype: boolean
        """
        for mandate_data in self.read(cr, uid, ids, ['deadline_date'],
                                      context=context):
            deadline = datetime.strptime(mandate_data['deadline_date'],
                                         DEFAULT_SERVER_DATE_FORMAT)
            if datetime.strptime(fields.datetime.now(),
                                 DEFAULT_SERVER_DATETIME_FORMAT) >= deadline:
                end_date = mandate_data['deadline_date']
            else:
                end_date = fields.datetime.now()
            self.action_invalidate(cr,
                                   uid,
                                   [mandate_data['id']],
                                   context=context,
                                   vals={'end_date': end_date})

        return True

# orm methods
    def create(self, cr, uid, vals, context=None):
        res = super(abstract_mandate, self).create(cr,
                                                   uid,
                                                   vals,
                                                   context=context)
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for mandate in self.browse(cr, uid, ids, context=context):
            display_name = u'{name} ({mandate_category})'.format(
                             name=mandate.partner_id.name,
                             mandate_category=mandate.mandate_category_id.name)
            res.append((mandate['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            partner_ids = self.pool.get('res.partner').search(
                                                  cr,
                                                  uid,
                                                  [('name', operator, name)],
                                                  context=context)
            category_ids = self.pool.get('mandate.category').search(
                                                    cr,
                                                    uid,
                                                    [('name', operator, name)],
                                                    context=context)
            ids = self.search(cr, uid, ['|',
                                        ('partner_id', 'in', partner_ids),
                                        ('mandate_category_id', 'in',
                                         category_ids)] + args,
                                         limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

# public methods

    def get_duplicate_ids(self, cr, uid, value, context=None):
        reset_ids = []
        duplicate_ids = []
        mandate_dataset = self._get_discriminant_model().search_read(
                                                 cr,
                                                 uid,
                                                 [(self._discriminant_field,
                                                   '=', value)],
                                                 ['mandate_category_id',
                                                  'start_date',
                                                  'deadline_date',
                                                  'is_duplicate_detected'],
                                                 context=context)
        for mandate_data in mandate_dataset:
            category = self.pool.get('mandate.category').browse(
                                        cr,
                                        uid,
                                        mandate_data['mandate_category_id'][0],
                                        context=context)
            if category.exclusive_category_m2m_ids:
                mandate_ids = self._get_discriminant_model().search(
                        cr,
                        uid,
                        [(self._discriminant_field,
                          '=', value),
                        ('mandate_category_id',
                         'in',
                         [exclu.id for
                                   exclu
                                   in category.exclusive_category_m2m_ids]),
                        ('start_date',
                         '<=',
                         mandate_data['deadline_date']),
                        ('deadline_date',
                         '>=',
                         mandate_data['start_date'])],
                        context=context)
                if mandate_ids:
                    mandate_ids.append(mandate_data['id'])
                    for mandate_id in mandate_ids:
                        if not(mandate_id in duplicate_ids):
                            duplicate_ids.append(mandate_id)
                        if mandate_id in reset_ids:
                            reset_ids.remove(mandate_id)
                elif mandate_data['is_duplicate_detected']:
                    reset_ids.append(mandate_data['id'])

            elif mandate_data['is_duplicate_detected']:
                reset_ids.append(mandate_data['id'])

        return reset_ids, duplicate_ids

    def detect_and_repair_duplicate(self, cr, uid, vals, context=None,
                                    detection_model=None, columns_to_read=[],
                                    model_id_name=None):
        """
        ===========================
        detect_and_repair_duplicate
        ===========================
        Detect automatically duplicates (setting the is_duplicate_detected
        flag)
        Repair orphan allowed or detected duplicate (resetting the
        corresponding flag)
        :param vals: discriminant values
        :type vals: list
        """
        super(abstract_mandate, self).detect_and_repair_duplicate(
                                    cr, uid, vals, context=context,
                                    columns_to_read=['model', 'mandate_id'],
                                    model_id_name='mandate_id')

    def process_finish_and_invalidate_mandates(self, cr, uid, context=None):
        """
        ======================================
        process_finish_and_invalidate_mandates
        ======================================
        This method is used to finish and invalidate mandates after deadline
        date
        :rparam: True
        :rtype: boolean
        """
        SQL_QUERY = """
            SELECT mandate.id
                FROM %s as mandate
                WHERE mandate.deadline_date < current_date
                  AND mandate.end_date IS NULL
          """
        cr.execute(SQL_QUERY % (self._name.replace('.', '_')))
        mandate_ids = self.search(cr,
                                  uid,
                                  [('id',
                                    'in',
                                    [mandate[0] for mandate
                                                 in cr.fetchall()])],
                                  context=context)

        if mandate_ids:
            self.action_finish(cr, uid, mandate_ids, context=context)

        return True


class abstract_candidature(orm.AbstractModel):

    _name = 'abstract.candidature'
    _description = 'Abstract Candidature'
    _inherit = ['mozaik.abstract.model']

    _init_mandate_columns = ['mandate_category_id',
                             'partner_id',
                             'designation_int_assembly_id']
    _mandate_model = 'abstract.mandate'
    _mandate_form_view = 'abstract_mandate_form_view'

    _mandate_category_store_trigger = {}
    _designation_assembly_store_trigger = {}
    _mandate_start_date_store_trigger = {}

    _columns = {
        'unique_id': fields.integer("Unique id"),
        'partner_id': fields.many2one('res.partner',
                                      'Candidate',
                                      required=True,
                                      select=True,
                                      track_visibility='onchange'),
        'partner_name': fields.char('Candidate Name',
                                    size=128,
                                    required=True,
                                    track_visibility='onchange'),
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES,
                                  'Status',
                                  readonly=True,
                                  track_visibility='onchange',),
        'selection_committee_id': fields.many2one(
                                        'abstract.selection.committee',
                                        string='Selection Committee',
                                        required=True,
                                        select=True,
                                        track_visibility='onchange'),
        'mandate_start_date': fields.related(
                                     'selection_committee_id',
                                     'mandate_start_date',
                                     string='Mandate Start Date',
                                     type='date',
                                     store=_mandate_start_date_store_trigger),
        'mandate_category_id': fields.related(
                                      'selection_committee_id',
                                      'mandate_category_id',
                                      string='Mandate Category',
                                      type='many2one',
                                      relation="mandate.category",
                                      store=_mandate_category_store_trigger),
        'designation_int_assembly_id': fields.related(
                                  'selection_committee_id',
                                  'designation_int_assembly_id',
                                  string='Designation Assembly',
                                  type='many2one',
                                  relation="int.assembly",
                                  store=_designation_assembly_store_trigger),
        'is_selection_committee_active': fields.related(
                                    'selection_committee_id',
                                    'active',
                                    string='Is Selection Committee Active?',
                                    type='boolean',
                                    store=False),
        'mandate_ids': fields.one2many(_mandate_model,
                                       'candidature_id',
                                       'Abstract Mandates',
                                       domain=[('active', '<=', True)]),
    }

    _defaults = {
        'state': CANDIDATURE_AVAILABLE_STATES[0][0],
    }

# constraints

    def _check_partner(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_partner
        =================
        Check if partner doesn't have several candidatures in the same category
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        candidatures = self.browse(cr, uid, ids)
        for candidature in candidatures:
            if len(self.search(cr,
                               uid,
                               [('partner_id',
                                 '=', candidature.partner_id.id),
                                ('id', '!=', candidature.id),
                                ('mandate_category_id',
                                 '=',
                                 candidature.mandate_category_id.id)],
                               context=context)) > 0:
                return False

        return True

    _constraints = [
        (_check_partner,
         _("A candidature already exists for this partner in this category"),
         ['partner_id'])
    ]

    _unicity_keys = 'selection_committee_id, partner_id'

# orm methods

    def create(self, cr, uid, vals, context=None):
        if ('partner_name' not in vals) or\
           ('partner_name' in vals and not vals['partner_name']):
            vals['partner_name'] = self.onchange_partner_id(
                                                    cr,
                                                    uid,
                                                    False,
                                                    vals['partner_id'],
                                                    context
                                                    )['value']['partner_name']

        res = super(abstract_candidature, self).create(cr,
                                                       uid,
                                                       vals,
                                                       context=context)
        self.write(cr, uid, res, {'unique_id': res + self._unique_id_sequence})
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for candidature in self.browse(cr, uid, ids, context=context):
            display_name = u'{name} ({mandate_category})'.format(
                       name=candidature.partner_name\
                            or candidature.partner_id.name,
                       mandate_category=candidature.mandate_category_id.name)
            res.append((candidature['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            partner_ids = self.pool.get('res.partner').search(cr,
                                                              uid,
                                                              [('name',
                                                                operator,
                                                                name)],
                                                              context=context)
            category_ids = self.pool.get('mandate.category').search(
                                                            cr,
                                                            uid,
                                                            [('name',
                                                              operator,
                                                              name)],
                                                            context=context)
            ids = self.search(cr, uid, ['|',
                                        '|',
                                        ('partner_name', operator, name),
                                        ('partner_id', 'in', partner_ids),
                                        ('mandate_category_id',
                                         'in', category_ids)] + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

# view methods: onchange, button

    def action_elected(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'elected'})
        for candidature in self.browse(cr, uid, ids, context):
            if candidature.selection_committee_id.auto_mandate:
                self.create_mandate_from_candidature(cr,
                                                     uid,
                                                     candidature.id,
                                                     context)
        return True

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = {}
        partner_model = self.pool.get('res.partner')
        partner = partner_model.browse(cr, uid, partner_id, context)

        res['value'] = dict(
                        partner_name=partner_model.build_name(
                                                        partner,
                                                        capitalize_mode=True)\
                                                        or False,)
        return res

    def button_create_mandate(self, cr, uid, ids, context=None):
        for candidature_id in ids:
            mandate_id = self.create_mandate_from_candidature(cr,
                                                              uid,
                                                              candidature_id,
                                                              context)

        return self.pool.get(self._mandate_model).display_object_in_form_view(
                                                            cr,
                                                            uid,
                                                            mandate_id,
                                                            context=context)

    def create_mandate_from_candidature(self, cr, uid, candidature_id,
                                        context=None):
        """
        ==============================
        create_mandate_from_candidature
        ==============================
        Return Mandate id create on base of candidature id
        :rparam: mandate id
        :rtype: id
        """
        mandate_pool = self.pool.get(self._mandate_model)
        committee_pool = self.pool.get(self._selection_committee_model)
        candidature_data = self.read(cr, uid, candidature_id, [], context)
        res = False
        mandate_values = {}
        for column in self._init_mandate_columns:
            if column in mandate_pool._columns:
                if self._columns[column]._type == 'many2one':
                    mandate_values[column] = candidature_data[column][0]
                else:
                    mandate_values[column] = candidature_data[column]

        if mandate_values:
            committee_data = committee_pool.read(
                                 cr,
                                 uid,
                                 candidature_data['selection_committee_id'][0],
                                 ['mandate_start_date',
                                  'mandate_deadline_date'],
                                 context=context)
            mandate_values['start_date'] = committee_data['mandate_start_date']
            mandate_values['deadline_date'] =\
                                        committee_data['mandate_deadline_date']
            mandate_values['candidature_id'] = candidature_data['id']
            res = mandate_pool.create(cr, uid, mandate_values, context)
        return res
