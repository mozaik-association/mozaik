# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression

from odoo.addons.mass_mailing.models.mailing import (
    MASS_MAILING_BUSINESS_MODELS as BASE_MASS_MAILING_BUSINESS_MODELS,
)

MASS_MAILING_BUSINESS_MODELS = BASE_MASS_MAILING_BUSINESS_MODELS + ["distribution.list"]


class MassMailing(models.Model):
    _inherit = "mailing.mailing"

    mailing_model_id = fields.Many2one(
        domain=[("model", "in", MASS_MAILING_BUSINESS_MODELS)]
    )

    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list", string="Distribution List",
    )

    @api.depends("mailing_model_id")
    def _compute_model(self):
        super(MassMailing, self)._compute_model()
        for record in self:
            if record.mailing_model_name == "distribution.list":
                record.mailing_model_real = "res.partner"

    @api.depends("mailing_model_name", "contact_list_ids", "distribution_list_id")
    def _compute_mailing_domain(self):
        super(MassMailing, self)._compute_mailing_domain()

    def _get_default_mailing_domain(self):
        mailing_domain = super(MassMailing, self)._get_default_mailing_domain()

        if self.mailing_model_name == "distribution.list" and self.distribution_list_id:
            # from _get_target_from_distribution_list we get the concerned virtual.target
            # records, but we are interested into the corresponding res.partner records
            target_ids = self.distribution_list_id._get_target_from_distribution_list()
            if target_ids._name != "res.partner":
                target_ids = target_ids.mapped("partner_id")
            mailing_domain = expression.AND(
                [[("id", "in", target_ids.ids,)], mailing_domain]
            )

        return mailing_domain

    def update_opt_out(self, email, res_ids, value):
        """
        Unsubscribe from distribution list if any
        :param email: string
        :param res_ids: list
        :param value: boolean
        """
        self.ensure_one()
        if self.distribution_list_id:
            # opt-out is delegated to the distribution list
            return self.distribution_list_id._update_opt(res_ids)
        return super().update_opt_out(email, res_ids, value)

    def _process_mass_mailing_queue(self):
        """
        Recompute mailing domains for mass mailings whose mailing model
        is distribution.list:
        """
        mass_mailings = self.search(
            [
                ("mailing_model_name", "=", "distribution.list"),
                ("state", "in", ("in_queue", "sending"),),
            ]
        )

        mass_mailings._compute_mailing_domain()
        super()._process_mass_mailing_queue()
