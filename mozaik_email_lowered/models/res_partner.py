# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):

    _name = "res.partner"
    _inherit = ["res.partner", "mozaik.lowered.email.mixin"]
