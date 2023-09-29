# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    amount = fields.Float(digits="Product Price", copy=False, tracking=True)
    reference = fields.Char(copy=False, tracking=True)
    promise = fields.Boolean(
        string="Just a promise", compute="_compute_promise", store=True, copy=False
    )
    payment_date = fields.Date(copy=False)
    is_paid = fields.Boolean(string="Paid", compute="_compute_is_paid")

    _sql_constraints = [
        (
            "donation",
            "CHECK (active IS FALSE OR involvement_type IS NULL OR "
            "involvement_type NOT IN ('donation') OR amount > 0.0)",
            "For a donation amount must be positive !",
        ),
    ]

    @api.depends("payment_date", "involvement_type")
    def _compute_promise(self):
        for involvement in self:
            involvement.promise = (
                involvement.involvement_type == "donation"
                and not involvement.payment_date
            )

    @api.depends("promise", "involvement_type")
    def _compute_is_paid(self):
        for inv in self:
            if inv.involvement_type == "donation":
                inv.is_paid = not inv.promise
            else:
                inv.is_paid = False
