# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


SELECTION_COMMITTEE_AVAILABLE_STATES = [
    ('draft', 'In Progress'),
    ('done', 'Closed'),
]
selection_committee_available_states = dict(
    SELECTION_COMMITTEE_AVAILABLE_STATES)


class AbstractSelectionCommittee(models.Model):
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
                raise osv.except_osv(
                    _('Operation Forbidden!'),
                    _('Some candidatures are still in "declared" state'))
        return res

    _columns = {
        'state': fields.selection(SELECTION_COMMITTEE_AVAILABLE_STATES,
                                  'Status',
                                  readonly=True,
                                  track_visibility='onchange', ),
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
        uid = SUPERUSER_ID
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
                name=committee.name, )
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
            ids = self.search(
                cr, uid, ['|',
                          ('name', operator, name),
                          ('assembly_id', 'in', assembly_ids)] + args,
                limit=limit, context=context)
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
                self.pool.get(
                    self._candidature_model).signal_workflow(
                    cr,
                    uid,
                    self._get_suggested_candidatures(
                        cr,
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
            values = dict(
                sta_assembly_category_id=(
                        mandate_category.sta_assembly_category_id.id or False),
                int_assembly_category_id=(
                        mandate_category.int_assembly_category_id.id or False),
                ext_assembly_category_id=(
                        mandate_category.ext_assembly_category_id.id or False),
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

            res['value'] = dict(
                assembly_category_id=assembly.assembly_category_id.id,
                mandate_category_id=mandate_category_id)

            if self.pool.get(self._assembly_model)._columns.get(
                    'designation_int_assembly_id'):
                res['value']['designation_int_assembly_id'] = \
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
            self.pool.get('ir.config_parameter').sudo().get_param(
                cr,
                uid,
                self._parameters_key,
                60))

        for committee in self.browse(cr, uid, committee_ids, context=context):
            limit_date = datetime.strptime(
                committee.expire_date,
                DEFAULT_SERVER_DATETIME_FORMAT) \
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
