# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class DistributionListLine(models.Model):

    _inherit = "distribution.list.line"

    @api.model
    def _get_src_model_names(self):
        """
        Add a new virtual src model to list of valid models
        :return: list of string
        """
        res = super()._get_src_model_names()
        return res + ["virtual.partner.mass.mailing"]
