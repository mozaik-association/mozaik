# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IntSelectionCommittee(models.Model):
    _name = "int.selection.committee"
    _description = "Selection Committee"
    _inherit = ["abstract.selection.committee"]
    _order = "assembly_id, mandate_start_date, mandate_category_id, name"
    _unicity_keys = "assembly_id, mandate_start_date, mandate_category_id, name"

    _candidature_model = "int.candidature"
    _assembly_model = "int.assembly"
    _assembly_category_model = "int.assembly.category"
    _parameters_key = "int_candidature_invalidation_delay"

    mandate_category_id = fields.Many2one(domain=[("type", "=", "int")])
    assembly_id = fields.Many2one(
        comodel_name=_assembly_model,
        string="Internal Assembly",
        domain=[("designation_int_assembly_id", "!=", False)],
    )
    candidature_ids = fields.One2many(
        comodel_name=_candidature_model,
        string="Internal Candidatures",
        context={"force_recompute": True},
    )
    assembly_category_id = fields.Many2one(
        comodel_name=_assembly_category_model,
        related="mandate_category_id.int_assembly_category_id",
        string="Internal Assembly Category",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="int_selection_committee_res_partner_rel",
        column1="committee_id",
        column2="partner_id",
        string="Members",
        domain=[("is_company", "=", False)],
    )
