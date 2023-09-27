# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import hashlib
import hmac
import logging

from odoo import http
from odoo.http import request
from odoo.tools.float_utils import float_repr

from odoo.addons.payment.controllers.portal import (
    PaymentProcessing,
    WebsitePayment as BaseWebsitePayment,
)

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
                    "involvement_id": kw.get("involvement_id"),
                    "display_reference": involvement._compute_default_donation_reference(),
                }
            )
        return res

    @http.route()
    def transaction(
        self, acquirer_id, reference, amount, currency_id, partner_id=False, **kwargs
    ):
        """
        Add the related involvement on the payment transaction.
        We have no other choice than overriding Odoo's code.
        """
        involvement_id = kwargs.get("involvement_id")

        if not involvement_id:
            return super().transaction(
                acquirer_id, reference, amount, currency_id, partner_id, **kwargs
            )

        # this is (again) a copy past of odoo code. search ACS
        acquirer = request.env["payment.acquirer"].browse(acquirer_id)

        values = {
            "acquirer_id": int(acquirer_id),
            "reference": reference,
            "amount": float(amount),
            "currency_id": int(currency_id),
            "partner_id": partner_id,
            "type": "form_save"
            if acquirer.save_token != "none" and partner_id
            else "form",
        }

        # ACS change invoice/order to membership
        if involvement_id:
            values["involvement_id"] = involvement_id

        reference_values = {"acquirer_id": acquirer_id}
        values["reference"] = request.env["payment.transaction"]._compute_reference(
            values=reference_values, prefix=reference
        )
        tx = (
            request.env["payment.transaction"]
            .sudo()
            .with_context(lang=None)
            .create(values)
        )
        secret = request.env["ir.config_parameter"].sudo().get_param("database.secret")
        token_str = "%s%s%s" % (
            tx.id,
            tx.reference,
            float_repr(tx.amount, precision_digits=tx.currency_id.decimal_places),
        )
        token = hmac.new(
            secret.encode("utf-8"), token_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        tx.return_url = "/website_payment/confirm?tx_id=%d&access_token=%s" % (
            tx.id,
            token,
        )

        PaymentProcessing.add_payment_transaction(tx)

        render_values = {
            "partner_id": partner_id,
            "type": tx.type,
        }
        if not partner_id:  # ACS
            # required field, not set if there is no partner
            render_values["billing_partner_country"] = request.env.company.country_id
        return acquirer.sudo().render(
            tx.reference, float(amount), int(currency_id), values=render_values
        )
