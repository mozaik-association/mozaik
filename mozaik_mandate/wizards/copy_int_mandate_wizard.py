# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CopyIntMandateWizard(models.TransientModel):
    _inherit = 'abstract.copy.mandate.wizard'
    _name = "copy.int.mandate.wizard"
    _description = 'Copy Int Mandate Wizard'

    _mandate_assembly_foreign_key = 'int_assembly_id'

    mandate_id = fields.Many2one(
        comodel_name='int.mandate',
        string='Internal Mandate')
    assembly_id = fields.Many2one(
        comodel_name='int.assembly',
        string='Internal Assembly')
    new_assembly_id = fields.Many2one(
        comodel_name='int.assembly',
        string='New Internal Assembly')
    instance_id = fields.Many2one(
        string='Internal Instance')
    int_assembly_category_id = fields.Many2one(
        related='new_mandate_category_id.int_assembly_category_id',
    )
