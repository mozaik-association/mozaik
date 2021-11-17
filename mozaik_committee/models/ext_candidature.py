# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from .abstract_candidature import AbstractCandidature


class ExtCandidature(models.Model):
    _name = "ext.candidature"
    _description = "External Candidature"
    _inherit = ["abstract.candidature"]
    _order = "ext_assembly_id, mandate_start_date, mandate_category_id, partner_id"
    _statechart_file = "mozaik_committee/data/ext_candidature.yml"

    _mandate_model = "ext.mandate"
    _selection_committee_model = "ext.selection.committee"
    _init_mandate_fields = list(AbstractCandidature._init_mandate_fields)
    _init_mandate_fields.extend(["ext_assembly_id", "months_before_end_of_mandate"])
    _allowed_inactive_link_models = [_selection_committee_model]
    _unique_id_sequence = 400000000

    selection_committee_id = fields.Many2one(comodel_name=_selection_committee_model)
    mandate_category_id = fields.Many2one(domain=[("type", "=", "ext")])
    ext_assembly_id = fields.Many2one(
        comodel_name="ext.assembly",
        related="selection_committee_id.assembly_id",
        string="External Assembly",
        store=True,
    )
    months_before_end_of_mandate = fields.Integer(
        related="ext_assembly_id.months_before_end_of_mandate",
        string="Alert Delay (#Months)",
    )
    mandate_ids = fields.One2many(
        comodel_name=_mandate_model, string="External Mandates"
    )
