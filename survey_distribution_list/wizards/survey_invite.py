# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SurveyInvite(models.TransientModel):

    _inherit = "survey.invite"

    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list", string="Distribution List",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        compute="_compute_emails_and_partner_ids",
        store=True,
        readonly=False,
    )
    emails = fields.Text(
        compute="_compute_emails_and_partner_ids", store=True, readonly=False,
    )

    @api.depends("distribution_list_id")
    def _compute_emails_and_partner_ids(self):
        for rec in self:
            rec.partner_ids = False
            rec.emails = ""
            if rec.distribution_list_id:
                results = rec.distribution_list_id._get_target_from_distribution_list()
                emails = []
                if results._name != "res.partner":
                    available_fields = results._fields
                    if (
                        "partner_id" not in available_fields
                        and "email" not in available_fields
                    ):
                        # If there's no partner or no email on the model
                        # we can't use it to send the link to a survey
                        raise UserError(
                            _(
                                """The target model of the distribution list
                                is not compatible with this functionnality."""
                            )
                        )
                    if "partner_id" in available_fields:
                        results = results.mapped("partner_id")
                    if "email" in available_fields and "partner_id" in available_fields:
                        # If both partner_id and email are available on the model
                        # we don't want to send the link twice.
                        # To avoid that we only use the email of records with no partner
                        emails = results.filtered(lambda r: not r.partner_id).mapped(
                            "email"
                        )
                    if (
                        "email" in available_fields
                        and "partner_id" not in available_fields
                    ):
                        emails = results.mapped("email")
                rec.partner_ids = results
                rec.emails += ";".join(emails)
