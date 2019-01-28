# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CopyExtMandateWizard(models.TransientModel):

    _inherit = 'abstract.copy.mandate.wizard'
    _name = 'copy.ext.mandate.wizard'

    _mandate_assembly_foreign_key = 'ext_assembly_id'

    mandate_id = fields.Many2one(
        comodel_name='ext.mandate',
        string='External Mandate',
        readonly=True,
        ondelete='cascade')
    assembly_id = fields.Many2one(
        comodel_name='ext.assembly',
        string='External Assembly',
        readonly=True,
        ondelete='cascade')
    new_assembly_id = fields.Many2one(
        comodel_name='ext.assembly',
        string='External Assembly',
        ondelete='cascade')
    instance_id = fields.Many2one(
        comodel_name='int.instance',
        string='Internal Instance',
        ondelete='cascade')
