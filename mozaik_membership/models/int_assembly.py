# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IntAssembly(models.Model):

    _name = 'int.assembly'
    _inherit = ['int.assembly', 'assembly.mixin']
