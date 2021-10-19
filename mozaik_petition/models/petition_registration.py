# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PetitionRegistration(models.Model):
    """Store answers on attendees."""

    _name = "petition.registration"
    _description = "Petition Registration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    partner_id = fields.Many2one("res.partner", string="Signatory")
    lastname = fields.Char(
        string="Lastname", compute="_compute_lastname", store=True, readonly=False
    )
    firstname = fields.Char(
        string="Firstname", compute="_compute_firstname", store=True, readonly=False
    )
    name = fields.Char(
        string="Name",
        compute="_compute_name",
        inverse="_inverse_name_after_cleaning_whitespace",
        required=False,
        store=True,
        readonly=False,
    )
    email = fields.Char(
        string="Email",
        compute="_compute_email",
        required=False,
        store=True,
        readonly=False,
    )
    mobile = fields.Char(string="Mobile")
    zip = fields.Char(string="Zip")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        default=lambda self: self.env["res.country"].search(
            [("name", "ilike", "Belgium")]
        ),
    )
    date_open = fields.Date(
        string="Registration Date", default=lambda self: fields.Date.today()
    )

    petition_id = fields.Many2one(
        "petition.petition",
        string="Petition",
        required=True,
        states={"draft": [("readonly", False)]},
    )
    registration_answer_ids = fields.One2many(
        "petition.registration.answer", "registration_id", string="Attendee Answers"
    )

    @api.depends("partner_id.name")
    def _compute_firstname(self):
        for record in self:
            if record.partner_id:
                record.firstname = record.partner_id.firstname

    @api.depends("partner_id.name")
    def _compute_lastname(self):
        for record in self:
            if record.partner_id:
                record.lastname = record.partner_id.lastname

    @api.depends("partner_id.email")
    def _compute_email(self):
        for record in self:
            if record.partner_id.email:
                record.email = record.partner_id.email

    @api.depends("firstname", "lastname")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = self.env["res.partner"]._get_computed_name(
                record.lastname, record.firstname
            )

    def _inverse_name_after_cleaning_whitespace(self):
        for record in self:
            clean = self.env["res.partner"]._get_whitespace_cleaned_name(record.name)
            record.name = clean
            parts = self.env["res.partner"]._get_inverse_name(
                record.name, record.partner_id.is_company
            )
            record.lastname = parts["lastname"]
            record.firstname = parts["firstname"]

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # auto-trigger after_sub (on subscribe) mail schedulers, if needed
        onsubscribe_schedulers = rec.mapped("petition_id.petition_mail_ids").filtered(
            lambda s: s.interval_type == "after_sub"
        )
        onsubscribe_schedulers.sudo().execute()
        return rec

    def write(self, vals):
        rec = super().write(vals)
        # auto-trigger after_sub (on subscribe) mail schedulers, if needed
        onsubscribe_schedulers = self.mapped("petition_id.petition_mail_ids").filtered(
            lambda s: s.interval_type == "after_sub"
        )
        onsubscribe_schedulers.sudo().execute()
        return rec


class PetitionRegistrationAnswer(models.Model):
    """Represents the user input answer for a single event.question"""

    _name = "petition.registration.answer"
    _description = "Petition Registration Answer"

    question_id = fields.Many2one(
        "petition.question",
        ondelete="restrict",
        required=True,
        domain="[('petition_id', '=', petition_id)]",
    )
    registration_id = fields.Many2one(
        "petition.registration", required=True, ondelete="cascade"
    )
    partner_id = fields.Many2one("res.partner", related="registration_id.partner_id")
    petition_id = fields.Many2one(
        "petition.petition", related="registration_id.petition_id"
    )
    question_type = fields.Selection(related="question_id.question_type")
    value_answer_id = fields.Many2one(
        "petition.question.answer", string="Suggested answer"
    )
    value_text_box = fields.Text("Text answer")
    value_tickbox = fields.Boolean("Tickbox")
    is_mandatory = fields.Boolean(related="question_id.is_mandatory")

    _sql_constraints = [
        (
            "value_check",
            "CHECK(value_tickbox IS NOT NULL OR "
            "value_answer_id IS NOT NULL OR "
            "COALESCE(value_text_box, '') <> '')",
            "There must be a suggested value, a text value or a tickbox value.",
        )
    ]

    @api.constrains("value_tickbox")
    def _check_value_tickbox(self):
        for record in self:
            if record.is_mandatory and not record.value_tickbox:
                raise ValidationError(
                    _("At least one mandatory tickbox is not checked.")
                )
