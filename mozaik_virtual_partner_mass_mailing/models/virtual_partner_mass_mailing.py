# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerMassMailing(models.Model):
    _name = "virtual.partner.mass.mailing"
    _inherit = "abstract.virtual.model"
    _description = "Partner/Mass Mailing"
    _auto = False

    mass_mailing_id = fields.Many2one(
        "mailing.mailing", string="Corresponding mass mailing"
    )
    mass_mailing_subject = fields.Char(string="Mass mailing subject")
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
        For mass mailing subject, as it is a translated field,
        take the translated value in the ir_translation table.
        :return: str
        """
        select = (
            super()._get_select()
            + """,
            mt.id as mailing_trace_id,
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
            mt.failure_type,
            CASE
                WHEN t.value IS NOT NULL
                THEN t.value
                ELSE mm.subject
            END as mass_mailing_subject"""
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
        JOIN res_partner p ON (mt.res_id = p.id)
        LEFT JOIN mailing_mailing mm ON (mm.id = mt.mass_mailing_id)
        JOIN ir_translation t ON (t.res_id = mm.id)
        """
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return (
            "WHERE mt.model = 'res.partner' "
            "AND p.active = TRUE "
            "AND p.identifier IS NOT NULL "
            "AND p.identifier != '0' "
            "AND mm.active = TRUE "
            "AND t.name='mailing.mailing,subject' "
            "AND t.lang=%(user_lang)s "
        )

    @api.model
    def _get_query_parameters(self, parameter=False):
        values = super()._get_query_parameters(parameter)
        values["user_lang"] = "fr_FR"
        return values

    @api.model
    def _get_order_by(self):
        """
        Since several records can have the same partner_id,
        ORDER BY 'partner_id' doesn't give always the same
        ordering between records having the same partner_id.
        We thus need to find a unique way to determine the ids
        and order the records.
        """
        return "mailing_trace_id"
