# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CopyExtMandateWizard(models.TransientModel):

    _inherit = "abstract.copy.mandate.wizard"
    _name = "copy.ext.mandate.wizard"
    _description = "Copy Ext Mandate Wizard"

    _mandate_assembly_foreign_key = "ext_assembly_id"

    mandate_id = fields.Many2one(comodel_name="ext.mandate", string="External Mandate")
    assembly_id = fields.Many2one(
        comodel_name="ext.assembly", string="External Assembly"
    )
    new_assembly_id = fields.Many2one(
        comodel_name="ext.assembly", string="New External Assembly"
    )
    instance_id = fields.Many2one(string="Internal Instance")
    ext_assembly_category_id = fields.Many2one(
        related="new_mandate_category_id.ext_assembly_category_id",
    )
