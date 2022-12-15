# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    bank_account_number = fields.Char("Bank Account Number")

    def _check_auto_validate(self, auto_val):
        self.ensure_one()
        auto_val, failure_reason = super()._check_auto_validate(auto_val)
        if auto_val and self.bank_account_number:
            partner_bank = self.env["res.partner.bank"].search(
                [
                    ("acc_number", "=ilike", self.bank_account_number),
                    ("partner_id", "!=", self.partner_id.id),
                ],
                limit=1,
            )
            if partner_bank:
                auto_val = False
                failure_reason = _(
                    "Bank account already linked to partner {name} ({id})"
                ).format(
                    name=partner_bank.partner_id.name, id=partner_bank.partner_id.id
                )
        return auto_val, failure_reason

    def validate_request(self):
        res = super().validate_request()
        for mr in self.filtered("bank_account_number"):
            if not mr.partner_id:
                raise ValidationError(
                    _("Membership request must have a partner to link account number")
                )
            partner_bank = self.env["res.partner.bank"].search(
                [("acc_number", "=ilike", mr.bank_account_number)]
            )
            if not partner_bank:
                partner_bank = self.env["res.partner.bank"].create(
                    {
                        "acc_number": mr.bank_account_number,
                        "partner_id": mr.partner_id.id,
                    }
                )
            elif partner_bank.partner_id != mr.partner_id:
                raise ValidationError(
                    _(
                        "Bank account {acc_number} already linked "
                        "to partner {name} ({id})"
                    ).format(
                        acc_number=partner_bank.acc_number,
                        name=partner_bank.partner_id.name,
                        id=partner_bank.partner_id.id,
                    )
                )
            if not partner_bank.mandate_ids.filtered(lambda m: m.state == "valid"):
                self.env["account.banking.mandate"].create(
                    {
                        "type": "recurrent",
                        "recurrent_sequence_type": "recurring",
                        "partner_bank_id": partner_bank.id,
                        "signature_date": fields.Date.today(),
                        "state": "valid",
                    }
                )
        return res
