# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta
from datetime import datetime


SELECTION_COMMITTEE_AVAILABLE_STATES = [
    ('draft', 'In Progress'),
    ('done', 'Closed'),
]


class AbstractSelectionCommittee(models.Model):
    _name = 'abstract.selection.committee'
    _description = 'Abstract Selection Committee'
    _inherit = ['mozaik.abstract.model']
    _unicity_keys = 'N/A'

    _candidature_model = 'abstract.candidature'
    _assembly_model = 'abstract.assembly'
    _assembly_category_model = 'abstract.assembly.category'
    _parameters_key = False

    state = fields.Selection(
        selection=SELECTION_COMMITTEE_AVAILABLE_STATES,
        string="Status",
        readonly=True,
        tracking=True,
        default=SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
    )
    mandate_category_id = fields.Many2one(
        comodel_name="mandate.category",
        string="Mandate Category",
        required=True,
        tracking=True,
    )
    assembly_id = fields.Many2one(
        comodel_name=_assembly_model,
        string="Abstract Assembly",
        tracking=True,
    )
    candidature_ids = fields.One2many(
        comodel_name=_candidature_model,
        inverse_name="selection_committee_id",
        string="Abstract Candidatures",
        domain=[("active", "<=", True)],
        copy=False,
    )
    assembly_category_id = fields.Many2one(
        comodel_name=_assembly_category_model,
        string="Abstract Assembly Category",
    )
    designation_int_assembly_id = fields.Many2one(
        comodel_name="int.assembly",
        string="Designation Assembly",
        required=True,
        tracking=True,
        domain=[("is_designation_assembly", "=", True)]
    )
    decision_date = fields.Date(
        string="Designation Date",
        tracking=True,
        copy=False,
    )
    mandate_start_date = fields.Date(
        string="Mandates Start Date",
        required=True,
        tracking=True,
    )
    mandate_deadline_date = fields.Date(
        string="Mandates Deadline Date",
        required=True,
        tracking=True,
    )
    meeting_date = fields.Date(
        string="Meeting Date",
        tracking=True,
        copy=False,
    )
    name = fields.Char(
        string="Name",
        size=128,
        index=True,
        required=True,
        tracking=True,
    )
    note = fields.Text(string="Notes", tracking=True, copy=False)
    auto_mandate = fields.Boolean(
        string="Create Mandates after Election",
        default=False,
    )

    # constraints

    _sql_constraints = [
        ('date_check', "CHECK(mandate_start_date <= mandate_deadline_date)",
         "The start date must be anterior to the deadline date."),
    ]

    @api.constrains("state", "decision_date")
    def _check_decision_date(self):
        """
        ====================
        _check_decision_date
        ====================
        Check if decision_date is not null when accepting the proposal
        """
        for committee in self:
            if committee.state == 'done' and not committee.decision_date:
                raise ValidationError(
                    "A decision date is mandatory when accepting "
                    "the proposal of the committee"
                )

    # orm methods

    def name_get(self):
        res = []
        for committee in self:
            display_name = u"{assembly}/{start} ({name})".format(
                assembly=committee.assembly_id.name,
                start=committee.mandate_start_date or False,
                name=committee.name,
            )
            res.append((committee["id"], display_name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            assembly_ids = self.env[self._assembly_model].search(
                [("name", operator, name)]
            )
            records = self.search(
                ['|',
                 ('name', operator, name),
                 ('assembly_id', 'in', assembly_ids)] + args,
                limit=limit)
        else:
            records = self.search(args, limit=limit)
        return records.ids

    def copy_data(self, default=None):
        if default is None:
            default = {}
        default.update({
            'active': True,
            'state': SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
        })
        res = super(AbstractSelectionCommittee, self).copy_data(default=default)

        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res

    # view methods: onchange, button

    def _get_suggested_candidatures(self):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        self.ensure_one()
        res = self.env[self._candidature_model]
        for candidature in self.candidature_ids:
            if candidature.state == 'rejected':
                continue
            elif candidature.state == 'suggested':
                res = res | candidature
            else:
                raise UserError(
                    "Operation Forbidden! "
                    "Some candidatures are still in 'declared' state"
                )
        return res

    def button_accept_candidatures(self):
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
        for committee in self:
            committee._get_suggested_candidatures().button_accept()
        self.action_invalidate({'state': 'done'})
        return True

    def button_refuse_candidatures(self):
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
        for committee in self:
            committee._get_suggested_candidatures().button_declare()
            self.write({'decision_date': False})
        return True

    @api.onchange("assembly_id")
    def onchange_assembly_id(self):
        self.ensure_one()
        if self.assembly_id:
            self.mandate_category_id = self.env["mandate.category"].search(
                [
                    (
                        self._mandate_catefory_foreign_key,
                        "=",
                        self.assembly_id.assembly_category_id.id,
                    )
                ], limit=1
            )
            if "designation_int_assembly_id" in self.env[self._assembly_model]._fields:
                self.designation_int_assembly_id = self.assembly_id.id

    # public methods

    def process_invalidate_candidatures_after_delay(self):
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
        self.env.cr.execute(SQL_QUERY % (self._name.replace('.', '_'),
                                self._candidature_model.replace('.', '_')))
        committees = self.search(
            [
                ("id", "in", [committee[0] for committee in self.env.cr.fetchall()]),
                ("active", "=", False),
            ]
        )

        invalidation_delay = int(
            self.env["ir.config_parameter"].sudo().get_param(self._parameters_key, 60)
        )

        for committee in committees:
            limit_date = datetime.strptime(
                committee.expire_date, DEFAULT_SERVER_DATETIME_FORMAT
            ) + relativedelta(days=invalidation_delay or 0.0)
            if (
                datetime.strptime(fields.datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
                >= limit_date
            ):
                self.env[self._candidature_model].action_invalidate(
                    [candidature.id for candidature in committee.candidature_ids]
                )

        return True
