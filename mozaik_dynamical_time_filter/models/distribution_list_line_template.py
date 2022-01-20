# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import normalize_domain
from odoo.tools.safe_eval import safe_eval


class DistributionListLineTemplate(models.Model):

    _inherit = "distribution.list.line.template"
    manually_edit_domain = fields.Boolean()
    domain_widget = fields.Char(string="Expression (widget)", default="[]")
    domain_handwritten = fields.Text(string="Expression (handwritten)", default="[]")
    domain = fields.Text(
        string="Expression", compute="_compute_domain", inverse="_inverse_domain"
    )

    @api.depends("domain_widget", "domain_handwritten")
    def _compute_domain(self):
        for record in self:
            record.domain = record._get_normalized_domain()

    def _inverse_domain(self):
        empty_domains = ["", "[]"]
        for record in self.filtered(
            lambda r: r.domain and r.domain not in empty_domains
        ):
            if record.manually_edit_domain:
                record.domain_handwritten = record.domain
            else:
                record.domain_widget = record.domain

    def _get_normalized_domain(self):
        self.ensure_one()
        domain = (
            self.domain_handwritten if self.manually_edit_domain else self.domain_widget
        )
        domain = safe_eval(
            domain,
            {
                "context_today": fields.Date.today,
                "relativedelta": relativedelta,
                "context_now": fields.Datetime.now,
            },
        )
        try:
            normalize_domain(domain)
        except AssertionError as assexc:
            raise ValidationError(_("Couldn't normalize the given domain")) from assexc
        return domain

    @api.onchange("manually_edit_domain")
    def _onchange_manually_edit_domain(self):
        if self.manually_edit_domain:
            self.domain_handwritten = self.domain_widget
        else:
            self.domain_widget = self.domain_handwritten

    @api.onchange("src_model_id")
    def _onchange_model_id(self):
        self.update(
            {
                "domain_handwritten": "[]",
                "domain_widget": "[]",
                "manually_edit_domain": False,
            }
        )

    @api.constrains("domain_handwritten")
    def _check_domain(self):
        for record in self.filtered("manually_edit_domain"):
            record._get_normalized_domain()
