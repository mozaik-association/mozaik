# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtAssembly(models.Model):

    _inherit = "ext.assembly"

    is_important = fields.Boolean(
        "Important Mandate", default=False, index=True, tracking=True
    )
