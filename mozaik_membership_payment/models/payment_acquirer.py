# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    can_be_used_for_membership = fields.Boolean(
        default=True,
        help="If ticked, this payment acquirer can be used to pay memberships",
    )
