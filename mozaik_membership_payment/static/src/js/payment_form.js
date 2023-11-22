/* eslint-disable */
odoo.define(
    "mozaik_membership_payment.payment_form",
    ["mozaik_payment.payment_form"],
    function (require) {
        "use strict";

        var paymentForm = require("mozaik_payment.payment_form");
        paymentForm.include({
            // Adding info about related membership / membership request
            _get_transaction_params: function (acquirer_id, form_save_token, options) {
                var res = this._super.apply(this, arguments);
                res["membership_id"] = options.membershipId;
                res["membership_request_id"] = options.membershipRequestId;
                return res;
            },
        });
    }
);
