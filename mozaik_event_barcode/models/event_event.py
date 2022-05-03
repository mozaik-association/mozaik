# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import normalize_domain
from odoo.tools.safe_eval import safe_eval

DEFAULT_VOTING_DOMAIN = "[]"


class EventEvent(models.Model):

    _inherit = "event.event"

    voting_domain = fields.Text(
        string="Domain for voting partners",
        help="Add a domain on virtual.partner.membership model "
        "to decide if an attendee has paid his contribution or not.",
        default=DEFAULT_VOTING_DOMAIN,
    )

    def _get_normalized_domain(self):
        self.ensure_one()
        domain = safe_eval(
            self.voting_domain,
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

    def _get_voting_partners(self):
        """
        Returns the list of ids corresponding to partners that
        match the voting domain.
        """
        self.ensure_one()
        voting_domain = self._get_normalized_domain()
        virtual_targets = self.env["virtual.partner.membership"].search(voting_domain)
        return virtual_targets.mapped("partner_id").ids

    def reopen_barcode_scanner(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "barcode.scanner",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_event_id": self.id,
            },
        }

    def open_barcode_scanner(self):
        self.ensure_one()
        res = self.reopen_barcode_scanner()
        res["context"].update(
            {
                "voting_partner_ids": self._get_voting_partners(),
            }
        )
        return res
