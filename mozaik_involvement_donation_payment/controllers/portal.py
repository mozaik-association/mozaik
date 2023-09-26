# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import http
from odoo.http import request

from odoo.addons.payment.controllers.portal import WebsitePayment as BaseWebsitePayment

_logger = logging.getLogger(__name__)


class WebsitePayment(BaseWebsitePayment):
    @http.route()
    def pay(
        self,
        reference="",
        order_id=None,
        amount=False,
        currency_id=None,
        acquirer_id=None,
        partner_id=False,
        access_token=None,
        **kw
    ):
        new_acquirer_id = acquirer_id
        # If type is partner involvement, take the acquirer on the involvement category
        if "involvement_id" in kw:
            involvement = (
                request.env["partner.involvement"]
                .sudo()
                .browse(int(kw["involvement_id"]))
            )
            new_acquirer_id = (
                involvement.involvement_category_id.payment_acquirer_id.id or None
            )

        res = super().pay(
            reference=reference,
            order_id=order_id,
            amount=amount,
            currency_id=currency_id,
            acquirer_id=new_acquirer_id,
            partner_id=partner_id,
            access_token=access_token,
            **kw
        )
        if "involvement_id" in kw:
            # Set display_reference to be the involvement reference
            # (if mozaik_membership_payment is installed it will be needed to display
            # the reference)
            res.qcontext.update(
                {
                    "display_reference": involvement._compute_default_donation_reference(),
                }
            )
        return res
