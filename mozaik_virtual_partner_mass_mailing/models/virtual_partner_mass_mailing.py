# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerMassMailing(models.Model):
    _name = "virtual.partner.mass.mailing"
    _inherit = "abstract.virtual.model"
    _description = "Partner/Mass Mailing"
    _auto = False

    int_instance_id = fields.Many2one(
        store=True,
        search=None,
    )
    mass_mailing_id = fields.Many2one(
        "mailing.mailing", string="Corresponding mass mailing"
    )
    mass_mailing_name = fields.Char(
        string="Mass mailing name", related="mass_mailing_id.name"
    )
    ignored = fields.Datetime(
        help="Date when the email has been invalidated. "
        "Invalid emails are blacklisted, opted-out or invalid email format"
    )
    scheduled = fields.Datetime(help="Date when the email has been created")
    sent = fields.Datetime(help="Date when the email has been sent")
    exception = fields.Datetime(
        help="Date of technical error leading to the email not being sent"
    )
    opened = fields.Datetime(help="Date when the email has been opened the first time")
    replied = fields.Datetime(
        help="Date when this email has been replied for the first time."
    )
    bounced = fields.Datetime(help="Date when this email has bounced.")
    clicked = fields.Datetime(
        help="Date when customer clicked on at least one tracked link"
    )
    state = fields.Selection(
        selection=[
            ("outgoing", "Outgoing"),
            ("exception", "Exception"),
            ("sent", "Sent"),
            ("opened", "Opened"),
            ("replied", "Replied"),
            ("bounced", "Bounced"),
            ("ignored", "Ignored"),
        ]
    )
    failure_type = fields.Selection(
        selection=[
            ("SMTP", "Connection failed (outgoing mail server problem)"),
            ("RECIPIENT", "Invalid email address"),
            ("BOUNCE", "Email address rejected by destination"),
            ("UNKNOWN", "Unknown error"),
        ],
        string="Failure type",
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = (
            super()._get_select()
            + """,
            p.int_instance_id,
            mt.mass_mailing_id,
            mt.ignored,
            mt.scheduled,
            mt.sent,
            mt.exception,
            mt.opened,
            mt.replied,
            mt.bounced,
            mt.clicked,
            mt.state,
            mt.failure_type"""
        )
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        from_query = """FROM
        mailing_trace as mt
JOIN res_partner AS p
    ON (mt.res_id = p.id)
    """
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE mt.model = 'res.partner' AND p.active = TRUE AND p.identifier > 0"
