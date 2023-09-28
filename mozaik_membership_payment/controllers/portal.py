import hashlib
import hmac

from odoo import http
from odoo.http import request
from odoo.tools.float_utils import float_repr

from odoo.addons.payment.controllers.portal import PaymentProcessing, WebsitePayment


class WebsitePaymentMozaik(WebsitePayment):
    def _filter_membership_acquirers(self, acquirers):
        membership_acquirers = []
        for acquirer in acquirers:
            if acquirer.can_be_used_for_membership:
                membership_acquirers.append(acquirer)
        return membership_acquirers

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
        if partner_id == "False":
            partner_id = False
        res = super(WebsitePaymentMozaik, self).pay(
            reference,
            order_id,
            amount,
            currency_id,
            acquirer_id,
            partner_id,
            access_token,
            **kw
        )
        res.qcontext.update(
            {
                "membership_id": kw.get("membership_id"),
                "membership_request_id": kw.get("membership_request_id"),
            }
        )
        if kw.get("membership_id") or kw.get("membership_request_id"):
            res.qcontext["acquirers"] = self._filter_membership_acquirers(
                res.qcontext.get("acquirers", [])
            )
        if kw.get("membership_id"):
            membership = (
                request.env["membership.line"]
                .sudo()
                .browse(int(kw.get("membership_id")))
            )
            # If the membership line is inactive and if the current
            # membership line is unpaid, change.
            if not membership.active:
                active_membership = (
                    request.env["membership.line"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", membership.partner_id.id),
                            ("active", "=", True),
                        ]
                    )
                )
                if len(active_membership) == 1 and not active_membership.paid:
                    return request.redirect(active_membership.payment_link)

            res.qcontext.update({"display_reference": membership.reference})
        elif kw.get("membership_request_id"):
            mr = (
                request.env["membership.request"]
                .sudo()
                .browse(int(kw.get("membership_request_id")))
            )
            res.qcontext.update({"display_reference": mr.reference})
        return res

    @http.route()
    def transaction(
        self, acquirer_id, reference, amount, currency_id, partner_id=False, **kwargs
    ):
        membership_id = kwargs.get("membership_id")
        membership_request_id = kwargs.get("membership_request_id")

        if not membership_id and not membership_request_id:
            return super(WebsitePaymentMozaik, self).transaction(
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
        if membership_id:
            values["membership_ids"] = [(6, 0, [membership_id])]
        if membership_request_id:
            values["membership_request_ids"] = [(6, 0, [membership_request_id])]

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
        if membership_request_id:
            email = (
                request.env["membership.request"]
                .sudo()
                .browse(membership_request_id)
                .email
            )
            if email:
                render_values["partner_email"] = email
        return acquirer.sudo().render(
            tx.reference, float(amount), int(currency_id), values=render_values
        )
