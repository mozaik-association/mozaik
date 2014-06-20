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
from datetime import date

from openerp.tools import logging
from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID

logger = logging.getLogger(__name__)


def make_webservice_error(object_id=False, session_id=False, error_code=False, error_text=False):
    return dict(response='WEBSERVICE-ERROR',
                object_id=object_id, session_id=session_id,
                error_code=error_code, error_text=error_text)


class WebServiceException(Exception):

    def __init__(self, session_id=False, object_id=False, error_code=False, error_text=False):
        self.session_id = session_id
        self.object_id = object_id
        self.error_code = error_code
        self.error_text = error_text


def web_service(func):
    def inner(self, cr, uid, *args, **kwargs):
        try:
            logger.info("WEB SERVICE REQUEST %s <- %s %s", func.__name__, repr(('self', 'cr', uid) + args), kwargs and repr(kwargs) or '')
            res = func(self, cr, uid, *args, **kwargs)
            logger.info("WEB SERVICE RESPONSE %s -> %s", func.__name__, repr(res))
            return res
        except WebServiceException as e:
            res = make_webservice_error(object_id=e.object_id,
                                  session_id=e.session_id,
                                  error_code=e.error_code,
                                  error_text=e.error_text)
            logger.warning("WEB SERVICE ERROR RESPONSE %s -> %s", func.__name__, repr(res), exc_info=True)
            cr.rollback()
            return res
        except Exception as e:
            res = WebServiceException(error_code='SYSTEM_ERROR',
                                 error_text=unicode(e))
            logger.error("WEB SERVICE SYSTEM ERROR RESPONSE %s -> %s", func.__name__, repr(res), exc_info=True)
            cr.rollback()
            return res
    return inner


class abstract_webservice(orm.AbstractModel):

    _name = 'abstract.webservice'


class membership_webservice(orm.Model):

    _name = 'membership.webservice'
    _inherit = ['abstract.webservice']

    @web_service
    def membership_request(self, cr, uid, lastname, firstname, gender, street, zip_code, town, status,\
                           day=False, month=False, year=False, email=False, mobile=False,
                           phone=False, interest=False, context=None):
        """
        ==================
        membership_request
        ==================
        Create a membership request.
        Search an existing partner with email-birth_date.
        Case where the partner exists: set the relation ``partner_id``
        with the found partner set other relation related to this partner too
        ``int_instance_id``
        ``address_local_zip_id``
        ``address_local_street_id``
        ``country_id``
        ``country_code``
        :type gender: char
        :param gender: 'f' or 'm'
        :type day: integer
        :param day: 01-31
        :type month: integer
        :param month: 01-12
        :type year: integer

        **Note**
        If day and month and year are set then birth_date is initialized with
        the collection of them
        """
        #birth_date
        #email (normalize)
        #search on birth_date/email
        #search on birth_date/firstname/lastname
        #search on email/firstname/lastname
        #
        membership_request = self.pool['membership.request']
        vals = membership_request.pre_process(cr, uid, lastname, firstname, gender, street, zip_code, town, status,\
                                              day=day, month=month, year=year, email=email, mobile=mobile, phone=phone,
                                              interest=interest, context=context)
        try:
            res = membership_request.create(cr, uid, vals, context=context)
        except Exception as e:
            raise WebServiceException(uid, '', 'ERROR-CREATE', e.message)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
