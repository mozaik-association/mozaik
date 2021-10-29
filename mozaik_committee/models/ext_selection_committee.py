# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtSelectionCommittee(models.Model):
    _name = "ext.selection.committee"
    _description = "Selection Committee"
    _inherit = ["abstract.selection.committee"]
    _order = "assembly_id, mandate_start_date, mandate_category_id, name"
    _unicity_keys = "assembly_id, mandate_start_date, mandate_category_id, name"

    _candidature_model = "ext.candidature"
    _assembly_model = "ext.assembly"
    _assembly_category_model = "ext.assembly.category"
    _parameters_key = "ext_candidature_invalidation_delay"

    mandate_category_id = fields.Many2one(domain=[("type", "=", "ext")])
    is_virtual = fields.Boolean(string="Is Virtual", default=True)
    assembly_id = fields.Many2one(
        comodel_name=_assembly_model,
        string="External Assembly",
    )
    candidature_ids = fields.One2many(
        comodel_name=_candidature_model,
        string="External Candidatures",
        context={"force_recompute": True},
    )
    assembly_category_id = fields.Many2one(
        comodel_name=_assembly_category_model,
        related="mandate_category_id.ext_assembly_category_id",
        string="External Assembly Category",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="ext_selection_committee_res_partner_rel",
        column1="committee_id",
        column2="partner_id",
        string="Members",
        domain=[("is_company", "=", False)],
    )
