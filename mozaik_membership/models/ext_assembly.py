# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ExtAssembly(models.Model):

    _name = "ext.assembly"
    _inherit = ["ext.assembly", "assembly.mixin"]
