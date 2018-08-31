# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from urllib.parse import urlencode, urljoin
from odoo import api, models


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def _get_unsubscribe_url(self, email_to):
        """
        Override native method to manage unsubscribe URL for distribution list
        case of newsletter.
        :param email_to: str
        :return:
        """
        self.ensure_one()
        mml = self.mailing_id
        if mml.distribution_list_id and mml.distribution_list_id.newsletter:
            res_id = self.res_id
            if self.model != 'res.partner':
                curr_obj = self.env[self.model]
                partner_path = mml.distribution_list_id.partner_path
                if hasattr(curr_obj, partner_path):
                    # Get partner_id
                    res_id = curr_obj.browse(res_id)[partner_path].id
                else:
                    # Do not set URL for newsletter if no partner_id
                    return False
            param_obj = self.env['ir.config_parameter']
            base_url = param_obj.get_param('web.base.url')
            vals = {
                'db': self.env.cr.dbname,
                'res_id': res_id,
                'email': email_to,
            }
            params = {
                'mailing_id': self.mailing_id.id,
                'params': urlencode(vals),
            }
            url = 'mail/newsletter/%(mailing_id)s/' \
                  'unsubscribe?%(params)s' % params
            full_url = urljoin(base_url, url)
            return full_url
        else:
            return super()._get_unsubscribe_url(email_to)
