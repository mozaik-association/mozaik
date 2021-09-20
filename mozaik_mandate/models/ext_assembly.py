# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ExtAssembly(models.Model):

    _inherit = 'ext.assembly'

    def _get_mandates(self):
        """
        return list of mandates linked to the assemblies
        """
        domain = [('ext_assembly_id', 'in', self.ids)]
        mandates = self.env['ext.mandate'].search(domain)
        return mandates
