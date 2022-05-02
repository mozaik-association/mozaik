from odoo import http

from odoo.addons.payment_paypal.controllers.main import PaypalController


class StripeControllerMozaik(PaypalController):
    @http.route()
    def paypal_cancel(self, **post):
        """When the user cancels its Paypal payment: GET on this route"""
        return super(PaypalController, self).paypal_cancel(**post)
