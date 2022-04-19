import werkzeug

from odoo import http
from odoo.http import request

from odoo.addons.payment_stripe.controllers.main import StripeController


class StripeControllerMozaik(StripeController):

    @http.route()
    def stripe_success(self, **kwargs):
        res = super(StripeControllerMozaik, self).stripe_success(**kwargs)
        transaction = request.env['payment.transaction'].search([('reference', '=', kwargs['reference'])])
        return werkzeug.utils.redirect('/payment/process?status=' + transaction.state)
