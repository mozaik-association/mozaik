/* eslint-disable */
odoo.define(
    "mozaik_involvement_donation_payment.payment_form",
    ["mozaik_payment.payment_form"],
    function (require) {
        "use strict";

        var paymentForm = require("mozaik_payment.payment_form");
        paymentForm.include({
            // Adding info about related involvement
            _get_transaction_params: function (acquirer_id, form_save_token, options) {
                var res = this._super.apply(this, arguments);
                res["involvement_id"] = options.involvementId;
                return res;
            },
        });
    }
);
