# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, models, _


class EmailCoordinate(models.Model):
    _inherit = 'email.coordinate'

    @api.model
    def get_url(self, path):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'external_website.base_url')
        if not base_url:
            raise exceptions.Warning(
                _('Please configure the base URL for the website'))
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        if not path.startswith('/'):
            path = '/' + path
        return base_url + path

    @api.model
    def check_mail_message_access(self, res_ids, operation, model_name=None):
        """
        :param res_ids: list of int
        :param operation: str
        :param model_name: str
        """
        context = self.env.context
        if context.get('active_model') == 'distribution.list' and \
                context.get('main_target_model') == 'email.coordinate':
            return None
        return super().check_mail_message_access(
            res_ids, operation, model_name=model_name)
