# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .abstract_candidature import AbstractCandidature

CANDIDATURE_AVAILABLE_SORT_ORDERS = {
    "elected": 0,
    "non-elected": 10,
    "designated": 20,
    "suggested": 22,
    "declared": 24,
    "rejected": 30,
    "draft": 90,
}


class StaCandidature(models.Model):
    _name = "sta.candidature"
    _description = "State Candidature"
    _inherit = ["abstract.candidature"]
    _order = "sta_assembly_id, electoral_district_id, legislature_id,\
                  mandate_category_id, sort_order, election_effective_position,\
                  election_substitute_position, list_effective_position,\
                  list_substitute_position, partner_id"
    _statechart_file = "mozaik_committee/data/sta_candidature.yml"

    _mandate_model = "sta.mandate"
    _selection_committee_model = "sta.selection.committee"
    _init_mandate_fields = list(AbstractCandidature._init_mandate_fields)
    _init_mandate_fields.extend(["legislature_id", "sta_assembly_id"])
    _allowed_inactive_link_models = [_selection_committee_model]
    _unique_id_sequence = 200000000

    state = fields.Selection(
        selection_add=[("designated", "Designated"), ("non-elected", "Non-Elected")]
    )
    selection_committee_id = fields.Many2one(comodel_name=_selection_committee_model)
    mandate_category_id = fields.Many2one(domain=[("type", "=", "sta")])
    sort_order = fields.Integer(
        compute="_compute_sort_order",
        string="Sort Order",
        store=True,
    )
    electoral_district_id = fields.Many2one(
        comodel_name="electoral.district",
        related="selection_committee_id.electoral_district_id",
        string="Electoral District",
        store=True,
    )
    legislature_id = fields.Many2one(
        comodel_name="legislature",
        related="selection_committee_id.legislature_id",
        string="Legislature",
        store=True,
    )
    sta_assembly_id = fields.Many2one(
        comodel_name="sta.assembly",
        related="selection_committee_id.assembly_id",
        string="State Assembly",
        store=True,
    )
    is_effective = fields.Boolean(string="Effective", tracking=True)
    is_substitute = fields.Boolean(string="Substitute", tracking=True)
    list_effective_position = fields.Integer(
        string="Position on Effectives List",
        group_operator="max",
        tracking=True,
        default=0,
    )
    list_substitute_position = fields.Integer(
        string="Position on Substitute List",
        group_operator="max",
        tracking=True,
        default=0,
    )
    election_effective_position = fields.Integer(
        string="Effective Position after Election",
        group_operator="max",
        tracking=True,
        default=0,
    )
    election_substitute_position = fields.Integer(
        string="Substitute Position after Election",
        group_operator="max",
        tracking=True,
        default=0,
    )
    effective_votes = fields.Integer(
        string="Effective Preferential Votes",
        tracking=True,
        default=0,
    )
    substitute_votes = fields.Integer(
        string="Substitute Preferential Votes",
        tracking=True,
        default=0,
    )
    is_legislative = fields.Boolean(
        related="sta_assembly_id.is_legislative",
        string="Is Legislative",
    )
    mandate_ids = fields.One2many(comodel_name=_mandate_model, string="State Mandates")

    @api.depends("state", "is_effective", "is_substitute")
    def _compute_sort_order(self):
        for cand in self:
            sort_order = CANDIDATURE_AVAILABLE_SORT_ORDERS.get(cand.state, 99)
            if cand.state == "non-elected":
                if cand.is_effective and not cand.is_substitute:
                    sort_order += 1
            elif not cand.is_effective and cand.is_substitute:
                sort_order += 1
            cand.sort_order = sort_order

    # view methods: onchange, button

    @api.onchange("is_effective", "is_substitute")
    def onchange_effective_substitute(self):
        self.ensure_one()
        if not self.is_effective and self.is_substitute:
            self.list_effective_position = False
        if not self.is_substitute:
            self.list_substitute_position = False

    def button_elected_candidature(self):
        for candidature in self:
            candidature.button_elected()
        return True

    def button_non_elected_candidature(self):
        for candidature in self:
            candidature.button_non_elected()
        return True
