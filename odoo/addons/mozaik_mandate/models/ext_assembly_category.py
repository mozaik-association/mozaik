# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtAssemblyCategory(models.Model):

    _inherit = 'ext.assembly.category'

    mandate_category_ids = fields.One2many(
        comodel_name='mandate.category',
        inverse_name='ext_assembly_category_id',
        string='Mandate Categories',
        domain=[('active', '=', True)])
    mandate_category_inactive_ids = fields.One2many(
        comodel_name='mandate.category',
        inverse_name='ext_assembly_category_id',
        string='Mandate Categories',
        domain=[('active', '=', False)])
