# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    internal_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal instance",
        ondelete="cascade",
    )

    def _get_default_mailing_domain(self):
        mailing_domain = super()._get_default_mailing_domain()

        if self.internal_instance_id:
            mailing_domain.append(
                ("int_instance_id", "child_of", self.internal_instance_id.ids)
            )

        return mailing_domain

    @api.depends(
        "mailing_model_name",
        "contact_list_ids",
        "distribution_list_id",
        "internal_instance_id",
    )
    def _compute_mailing_domain(self):
        super()._compute_mailing_domain()
