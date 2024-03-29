# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    def create(self, vals):
        res = super().create(vals)
        # When uploading an image in body_arch in a mass_mailing, res_model equals "model"
        # and not "mailing.mailing".
        public = res.filtered(
            lambda s: s.res_model
            in [
                "petition.petition",
                "survey.survey",
                "mailing.mailing",
                "mail.template",
                "model",
            ]
            and s.index_content == "image"
        )
        if public:
            public.write({"public": True})
        return res
