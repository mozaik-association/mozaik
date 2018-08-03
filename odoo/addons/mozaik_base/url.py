# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from urllib import urlencode
from urlparse import urljoin

_logger = logging.getLogger(__name__)


def get_document_url(self, cr, uid, model, object_id, context=None):
        """
        ================
        get_document_url
        ================
        Builds the Url to a document
        :type model: string
        :param model: model technical name
        :type object_id: integer
        :param object_id: document id
        :rtype: string
        :rparam: document url
        """
        base_url = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'web.base.url')
        # the parameters to encode for the query and fragment part of url
        query = {
            'db': cr.dbname,
        }
        fragment = {
            'action': 'mail.action_mail_redirect',
            'model': model,
            'res_id': object_id,
        }
        url = urljoin(
            base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return url
