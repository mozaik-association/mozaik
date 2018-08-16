# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, models, _
from openerp.exceptions import Warning


class EmailCoordinate(models.Model):

    _inherit = 'email.coordinate'

    @api.model
    def get_url(self, path):
        base_url = self.env['ir.config_parameter'].get_param(
            'external_website.base_url')
        if not base_url:
            raise Warning(
                _('Please configure the base URL for the website'))
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        if not path.startswith('/'):
            path = '/' + path
        return base_url + path

    # TODO was in the mozaik_email addon
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
