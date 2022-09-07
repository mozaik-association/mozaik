# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class InterestGroup(models.Model):

    _name = "interest.group"
    _description = "Interest Group"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "name"
    _order = "name"

    name = fields.Char(required=True)

    parent_id = fields.Many2one(
        comodel_name="interest.group",
        string="Parent Interest Group",
        index=True,
        ondelete="restrict",
    )
    child_ids = fields.One2many(
        comodel_name="interest.group",
        inverse_name="parent_id",
    )
    parent_path = fields.Char(index=True)

    _sql_constraints = [
        ("unique_name", "unique(name)", "Interest group name must be unique"),
    ]
