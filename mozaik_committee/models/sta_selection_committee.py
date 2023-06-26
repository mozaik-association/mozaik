# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StaSelectionCommittee(models.Model):
    _name = "sta.selection.committee"
    _description = "Selection Committee"
    _inherit = ["abstract.selection.committee"]
    _order = (
        "assembly_id, electoral_district_id, legislature_id, mandate_category_id, name"
    )
    _unicity_keys = (
        "assembly_id, electoral_district_id, legislature_id, mandate_category_id, name"
    )

    _candidature_model = "sta.candidature"
    _assembly_model = "sta.assembly"
    _assembly_category_model = "sta.assembly.category"
    _mandate_category_foreign_key = "sta_assembly_category_id"
    _parameters_key = "sta_candidature_invalidation_delay"

    mandate_category_id = fields.Many2one(domain=[("type", "=", "sta")])
    assembly_id = fields.Many2one(
        comodel_name=_assembly_model,
        string="State Assembly",
    )
    candidature_ids = fields.One2many(
        comodel_name=_candidature_model,
        string="State Candidatures",
        context={"force_recompute": True},
    )
    assembly_category_id = fields.Many2one(
        comodel_name=_assembly_category_model,
        related="mandate_category_id.sta_assembly_category_id",
        string="State Assembly Category",
    )
    electoral_district_id = fields.Many2one(
        comodel_name="electoral.district",
        string="Electoral District",
        tracking=True,
    )
    legislature_id = fields.Many2one(
        comodel_name="legislature",
        string="Legislature",
        tracking=True,
    )
    listname = fields.Char(
        string="Listname",
        size=128,
        tracking=True,
    )
    is_cartel = fields.Boolean(string="Is Cartel")
    cartel_composition = fields.Text(
        string="Cartel Composition",
        tracking=True,
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="sta_selection_committee_res_partner_rel",
        column1="committee_id",
        column2="partner_id",
        string="Members",
        domain=[("is_company", "=", False)],
    )

    # orm methods

    def name_get(self):
        res = []
        for committee in self:
            display_name = "{assembly}/{start} ({name})".format(
                assembly=committee.electoral_district_id.name
                or committee.assembly_id.name,
                start=committee.mandate_start_date or False,
                name=committee.name,
            )
            res.append((committee["id"], display_name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            assembly_ids = self.env["sta.assembly.category"].search(
                [("name", operator, name)]
            )
            district_ids = self.env["electoral.district"].search(
                [("name", operator, name)]
            )
            records = self.search(
                [
                    "|",
                    "|",
                    ("name", operator, name),
                    ("electoral_district_id", "in", district_ids.ids),
                    "&",
                    ("assembly_id", "in", assembly_ids.ids),
                    ("electoral_district_id", "=", False),
                ]
                + args,
                limit=limit,
            )
        else:
            records = self.search(args, limit=limit)
        return records.ids

    def copy(self, default=None):
        self.ensure_one()
        res = super(StaSelectionCommittee, self).copy(default=default)
        res.onchange_assembly_id()
        res.onchange_legislature_id()
        return res

    # view methods: onchange, button

    @api.onchange("electoral_district_id")
    def onchange_electoral_district_id(self):
        self.ensure_one()
        if self.electoral_district_id:
            self.assembly_id = self.electoral_district_id.assembly_id.id
            self.designation_int_assembly_id = (
                self.electoral_district_id.designation_int_assembly_id.id
            )
        else:
            self.assembly_id = False
            self.designation_int_assembly_id = False

    @api.onchange("legislature_id")
    def onchange_legislature_id(self):
        self.ensure_one()
        if self.legislature_id:
            self.mandate_start_date = self.legislature_id.start_date
            self.mandate_deadline_date = self.legislature_id.deadline_date
        else:
            self.mandate_start_date = False
            self.mandate_deadline_date = False

    @api.onchange("assembly_id")
    def onchange_assembly_id(self):
        self.ensure_one()
        super(StaSelectionCommittee, self).onchange_assembly_id()
        if self.assembly_id:
            legislature = self.env["legislature"].search(
                [
                    (
                        "power_level_id",
                        "=",
                        self.assembly_id.assembly_category_id.power_level_id.id,
                    ),
                    ("start_date", ">", fields.datetime.now()),
                ],
                limit=1,
            )
            self.legislature_id = legislature.id
        if self.electoral_district_id:
            self.designation_int_assembly_id = (
                self.electoral_district_id.designation_int_assembly_id.id
            )
