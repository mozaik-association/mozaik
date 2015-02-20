# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        # the parameters to encode for the query and fragment part of url
        query = {
            'db': cr.dbname,
        }
        fragment = {
            'action': 'mail.action_mail_redirect',
            'model': model,
            'res_id': object_id,
        }
        url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return url
