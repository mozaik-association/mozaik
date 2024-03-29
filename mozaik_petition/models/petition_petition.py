# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PetitionPetition(models.Model):

    _name = "petition.petition"
    _description = "Petition"
    _rec_name = "title"
    _order = "date_begin"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(default=True)
    title = fields.Char(string="Title", required=True, tracking=True)
    description = fields.Text(string="Description")
    summary = fields.Text(string="Summary")
    note = fields.Text(string="Notes", tracking=True)
    image = fields.Binary(string="Image")
    visible_on_website = fields.Boolean(string="Visible on website", default=True)
    date_begin = fields.Date(string="Beginning Date", required=True, tracking=True)
    date_end = fields.Date(string="Ending Date", required=True, tracking=True)
    date_publish = fields.Date(string="Publish Date")
    url = fields.Char(string="URL")
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("online", "Online"),
            ("not_active", "Not Active"),
        ],
        default="draft",
    )
    partner_ids = fields.Many2many("res.partner", string="Partners")
    milestone_ids = fields.One2many(
        "petition.milestone", "petition_id", string="Milestones"
    )
    question_ids = fields.One2many(
        "petition.question",
        "petition_id",
        string="Questions",
        copy=True,
        compute="_compute_question_ids",
        readonly=False,
        store=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        tracking=True,
    )
    registration_ids = fields.One2many(
        "petition.registration", "petition_id", string="Signatories"
    )
    signatory_count = fields.Integer(
        string="Number of signatories", compute="_compute_signatory_count", store=True
    )
    petition_type_id = fields.Many2one("petition.type", string="Petition Template")

    petition_mail_ids = fields.One2many(
        "petition.mail", "petition_id", string="Mail Schedule", copy=True
    )

    def _check_milestone_ids(self):
        mandatory_milestone = (
            self.sudo()
            .env["ir.config_parameter"]
            .get_param("petition.petition.mandatory.milestone")
        )
        if mandatory_milestone == "True" and not all(
            petition.milestone_ids for petition in self
        ):
            raise ValidationError(_("At least one milestone is mandatory on petitions"))

    def write(self, vals):
        """We add a check to prevent changing the template questions
        of a petition if there are already signatories."""
        for rec in self:
            if (
                "template_id" in vals
                and vals["template_id"] != rec.template_id.id
                and rec.signatory_count > 0
            ):
                raise ValidationError(
                    _(
                        "You cannot change the template questions "
                        "of a petition when there are signatories."
                    )
                )
        res = super(PetitionPetition, self).write(vals)
        self._check_milestone_ids()
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._check_milestone_ids()
        return res

    @api.depends("registration_ids")
    def _compute_signatory_count(self):
        for record in self:
            record.signatory_count = len(record.registration_ids)

    @api.model
    def _get_question_copy_values(self, question):
        """
        Returns a dictionary of fields (along with their value) to copy
        when loading a question from an petition type to a petition.
        """
        question.ensure_one()
        return {
            "title": question.title,
            "question_type": question.question_type,
            "sequence": question.sequence,
            "is_mandatory": question.is_mandatory,
            "answer_ids": [
                (
                    0,
                    0,
                    {
                        "name": answer.name,
                        "sequence": answer.sequence,
                    },
                )
                for answer in question.answer_ids
            ],
        }

    @api.depends("petition_type_id")
    def _compute_question_ids(self):
        """Update petition questions from its petition type. Depends are set only on
        petition_type_id itself to emulate an onchange. Changing petition type content
        itself should not trigger this method.

        When synchronizing questions, we delete all questions (since template_id becomes
        readonly when there are registered signatories) and copy type questions.
        """
        for petition in self:
            command = [(5, 0)]
            for question in petition.petition_type_id.question_ids:
                command += [(0, 0, self._get_question_copy_values(question))]
            petition.question_ids = command

    @api.constrains("date_begin", "date_end")
    def _check_closing_date(self):
        for petition in self:
            if petition.date_end < petition.date_begin:
                raise ValidationError(
                    _("The closing date cannot be earlier than the beginning date.")
                )

    def display_signatories_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Signatories",
            "res_model": "petition.registration",
            "domain": [("petition_id", "=", self.id)],
            "context": {"default_petition_id": self.id},
            "view_mode": "tree,form",
        }

    def send_mail_to_signatories(
        self, template_id, force_send=False, email_values=None
    ):
        for petition in self:
            for signatory in petition.registration_ids:
                self.env["mail.template"].browse(template_id).send_mail(
                    signatory.id, force_send=force_send, email_values=email_values
                )
