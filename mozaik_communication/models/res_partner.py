# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    distribution_list_opt_out_ids = fields.Many2many(
        comodel_name="distribution.list",
        relation="distribution_list_res_partner_out",
        column1="partner_id",
        column2="distribution_list_id",
        string="Opt-Out",
        domain=[("newsletter", "=", True)],
    )
    distribution_list_opt_in_ids = fields.Many2many(
        comodel_name="distribution.list",
        relation="distribution_list_res_partner_in",
        column1="partner_id",
        column2="distribution_list_id",
        string="Opt-In",
        domain=[("newsletter", "=", True)],
    )
    responsible_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible User (Communication)",
        index=True,
    )
    email_bounced = fields.Integer(default=0, string="Counter of bounced emails")
    email_bounced_description = fields.Char()

    postal_bounced = fields.Boolean(
        "Postal Bounced", compute="_compute_postal_bounced", store=True
    )
    last_postal_failure_date = fields.Datetime(
        "Last Postal Failure Date",
        copy=False,
        tracking=True,
    )

    @api.depends("last_postal_failure_date")
    def _compute_postal_bounced(self):
        for record in self:
            record.postal_bounced = False
            if record.last_postal_failure_date:
                record.postal_bounced = True

    _sql_constraints = [
        (
            "email_bounced_check",
            "CHECK(email_bounced >= 0)",
            "The number of bounced emails has to be non negative.",
        ),
    ]
