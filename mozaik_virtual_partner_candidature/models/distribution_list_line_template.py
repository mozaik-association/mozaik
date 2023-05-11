# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class DistributionListLineTemplate(models.Model):

    _inherit = "distribution.list.line.template"

    @api.model
    def _get_src_model_names(self):
        """
        Add a new virtual src model to list of valid models
        :return: list of string
        """
        res = super()._get_src_model_names()
        return res + ["virtual.partner.candidature"]
