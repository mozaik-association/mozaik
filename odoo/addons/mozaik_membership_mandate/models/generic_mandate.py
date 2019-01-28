# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class GenericMandate(models.Model):

    _inherit = 'generic.mandate'

    partner_instance_ids = fields.Many2many(
        related='partner_id.int_instance_ids',
        string='Partner Internal Instance')
