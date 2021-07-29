# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MandateCategory(models.Model):

    _inherit = 'mandate.category'

    sequence = fields.Integer(default=99999, string="Formal position")
