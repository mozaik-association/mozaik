# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_assembly = fields.Boolean(
        readonly=True,
        copy=False,
    )

    ext_assembly_ids = fields.One2many(
        comodel_name="ext.assembly",
        inverse_name="ref_partner_id",
        string="External Assemblies",
    )
