# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http


class MassMailController(http.Controller):

    @http.route(['/mail/newsletter/'
                 '<model("mail.mass_mailing"):mailing>/unsubscribe'],
                type='http', auth='none')
    def newsletter(self, mailing, email=None, res_id=None, **post):
        return mailing.sudo().try_update_opt(res_id)
