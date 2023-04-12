# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

CANDIDATURE_AVAILABLE_STATES = [
    ("draft", "Draft"),
    ("declared", "Declared"),
    ("designated", "Designated"),
    ("rejected", "Rejected"),
    ("elected", "Elected"),
    ("non-elected", "Non-Elected"),
]


class AbstractCandidature(models.Model):
    _name = "abstract.candidature"
    _description = "Abstract Candidature"
    _inherit = ["mozaik.abstract.model", "statechart.mixin"]
    _unicity_keys = "selection_committee_id, partner_id"

    _init_mandate_fields = [
        "mandate_category_id",
        "partner_id",
        "designation_int_assembly_id",
    ]
    _mandate_model = "abstract.mandate"

    unique_id = fields.Integer("Unique id", group_operator="min")
    partner_id = fields.Many2one(
        "res.partner", "Candidate", required=True, index=True, tracking=True
    )
    partner_id_domain = fields.Char(
        compute="_compute_partner_id_domain",
        readonly=True,
        store=False,
    )
    state = fields.Selection(
        CANDIDATURE_AVAILABLE_STATES,
        "Status",
        readonly=True,
        tracking=True,
        default="draft",
    )
    selection_committee_id = fields.Many2one(
        "abstract.selection.committee",
        string="Selection Committee",
        required=True,
        index=True,
        tracking=True,
    )
    int_instance_id = fields.Many2one(
        "int.instance", related="selection_committee_id.int_instance_id"
    )
    mandate_start_date = fields.Date(
        related="selection_committee_id.mandate_start_date",
        string="Mandate Start Date",
        store=True,
    )
    mandate_category_id = fields.Many2one(
        comodel_name="mandate.category",
        related="selection_committee_id.mandate_category_id",
        string="Mandate Category",
        store=True,
    )
    designation_int_assembly_id = fields.Many2one(
        comodel_name="int.assembly",
        related="selection_committee_id.designation_int_assembly_id",
        string="Designation Assembly",
        store=True,
    )
    is_selection_committee_active = fields.Boolean(
        related="selection_committee_id.active",
        string="Is Selection Committee Active?",
        type="boolean",
    )
    mandate_ids = fields.One2many(
        _mandate_model,
        "candidature_id",
        "Abstract Mandates",
        domain=[("active", "<=", True)],
    )
    # constraints

    @api.constrains("partner_id")
    def _check_partner(self):
        """
        =================
        _check_partner
        =================
        Check if partner doesn't have several candidatures in the same category
        """
        for candidature in self:
            if (
                len(
                    self.sudo().search(
                        [
                            ("partner_id", "=", candidature.partner_id.id),
                            ("id", "!=", candidature.id),
                            (
                                "mandate_category_id",
                                "=",
                                candidature.mandate_category_id.id,
                            ),
                        ]
                    )
                )
                > 0
            ):
                raise ValidationError(
                    _("A candidature already exists for this partner in this category")
                )

    # computes

    @api.depends("int_instance_id")
    def _compute_partner_id_domain(self):
        for rec in self:
            domain = [("is_company", "=", False)]
            if self.int_instance_id:
                domain.append(("int_instance_ids", "child_of", self.int_instance_id.id))
            rec.partner_id_domain = json.dumps(domain)

    # orm methods

    @api.model
    def create(self, vals):
        res = super(AbstractCandidature, self).create(vals)
        res.write({"unique_id": res.id + self._unique_id_sequence})
        res._sc_execute(res.sc_interpreter, "[auto]")
        return res

    def name_get(self):
        res = []
        for candidature in self:
            display_name = "{name} ({mandate_category})".format(
                name=candidature.partner_id.name,
                mandate_category=candidature.mandate_category_id.name,
            )
            res.append((candidature["id"], display_name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            partner_ids = self.env["res.partner"].search([("name", operator, name)])
            category_ids = self.env["mandate.category"].search(
                [("name", operator, name)]
            )
            records = self.search(
                [
                    "|",
                    "|",
                    ("partner_id", operator, name),
                    ("partner_id", "in", partner_ids),
                    ("mandate_category_id", "in", category_ids),
                ]
                + args,
                limit=limit,
            )
        else:
            records = self.search(args, limit=limit)
        return records.ids

    # view methods: onchange, button

    def action_elected(self):
        self.write({"state": "elected"})
        for candidature in self:
            candidature.create_mandate_from_candidature()
        return True

    def button_create_mandate(self):
        for candidature in self:
            mandate_id = candidature.create_mandate_from_candidature()

        return {
            "type": "ir.actions.act_window",
            "name": _("Mandate"),
            "res_model": self._mandate_model,
            "res_id": mandate_id.id,
            "view_mode": "form",
            "context": self.env.context,
        }

    def create_mandate_from_candidature(self):
        """
        ==============================
        create_mandate_from_candidature
        ==============================
        Return Mandate id create on base of candidature id
        :rparam: mandate id
        :rtype: mandate
        """
        self.ensure_one()
        mandate_model = self.env[self._mandate_model]
        res = False
        mandate_values = {}
        for field in self._init_mandate_fields:
            if field in mandate_model._fields:
                if isinstance(self._fields[field], fields.Many2one):
                    mandate_values[field] = self[field].id
                else:
                    mandate_values[field] = self[field]

        if mandate_values:
            mandate_values[
                "start_date"
            ] = self.selection_committee_id.mandate_start_date
            mandate_values[
                "deadline_date"
            ] = self.selection_committee_id.mandate_deadline_date
            mandate_values["candidature_id"] = self.id
            res = mandate_model.create(mandate_values)
        return res

    def button_declare_candidature(self):
        for candidature in self:
            candidature.button_declare()
        return True

    def button_designate_candidature(self):
        for candidature in self:
            candidature.button_designate()
        return True

    def button_reject_candidature(self):
        for candidature in self:
            candidature.button_reject()
        return True

    def button_elected_candidature(self):
        for candidature in self:
            if not candidature.selection_committee_id.decision_date:
                raise ValidationError(
                    _(
                        "A decision date is mandatory on the selection committee "
                        "when electing a candidature."
                    )
                )
            candidature.button_elected()
        return True

    def button_non_elected_candidature(self):
        for candidature in self:
            if not candidature.selection_committee_id.decision_date:
                raise ValidationError(
                    _(
                        "A decision date is mandatory on the selection committee "
                        "when non-electing a candidature."
                    )
                )
            candidature.button_non_elected()
        return True
