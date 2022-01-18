# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    def create(self, vals):
        res = super().create(vals)
        if res.res_model in ["petition.petition", "survey.survey"]:
            res.write({"public": True})
        return res
