# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IntAssembly(models.Model):

    _inherit = 'int.assembly'

    selection_committee_ids = fields.One2many(
        comodel_name="int.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees",
        domain=[("active", "=", True)],
    )
    selection_committee_inactive_ids = fields.One2many(
        comodel_name="int.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees (Inactive)",
        domain=[("active", "=", False)],
    )
