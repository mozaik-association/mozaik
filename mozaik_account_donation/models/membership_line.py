# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class MembershipLine(models.Model):
    _inherit = "membership.line"

    donation_move_ids = fields.Many2many(
        comodel_name="account.move",
        string="Donations",
        readonly=True,
        copy=False,
    )

    def _mark_as_paid(self, amount, move_id, bank_id=False):
        """
        When paying a membership line that is already paid, the amount is considered as
        a donation.
        """
        self.ensure_one()
        if self.paid:
            # IMPORTANT: do this before super, otherwise all membership lines will
            # be marked as paid.
            vals = {
                "price_paid": self.price_paid + amount,
            }
            if self.move_id.id != move_id and move_id not in self.donation_move_ids.ids:
                vals["donation_move_ids"] = [(4, move_id, 0)]
            self.write(vals)
        res = super()._mark_as_paid(amount, move_id, bank_id)

        return res
