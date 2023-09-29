/* eslint-disable */
odoo.define("mozaik_involvement_donation_payment.payment_form", function (require) {
    "use strict";

    var core = require("web.core");

    var _t = core._t;

    var paymentForm = require("payment.payment_form");
    var origGetTransactionParams = paymentForm.prototype._get_transaction_params;
    paymentForm.include({
        // Adding info about related involvement
        _get_transaction_params: function (acquirer_id, form_save_token, options) {
            var res = origGetTransactionParams(acquirer_id, form_save_token, options);
            res["involvement_id"] = options.involvementId;
            return res;
        },
    });
});
