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

from openerp.tools import logging
from openerp.osv import orm
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


class custom_webservice(orm.Model):

    _name = 'custom.webservice'

    @web_service
    def membership_request(self, cr, uid, lastname, firstname, gender, street, zip_code, town, status,\
                           day=False, month=False, year=False, email=False, mobile=False,
                           phone=False, interest=False, context=None):
        """
        ==================
        membership_request
        ==================
        Create a `membership.request` with the giving values
        """
        context = context or {}
        membership_request = self.pool['membership.request']
        vals = {
            'lastname': lastname,
            'firstname': firstname,
            'state': 'confirm',

            'gender': gender,
            'day': day,
            'month': month,
            'year': year,

            'request_status': status,
            'street_man': street,
            'zip_man': zip_code,
            'town_man': town,

            'mobile': mobile,
            'phone': phone,
            'email': email,

            'interests': interest,
        }
        if vals['request_status'] == 'm':
            vals['product_id'] = self.pool['product.product']._get_default_subscription(self, cr, uid, context=context)
        context['mode'] = 'ws'
        try:
            res = membership_request.create(cr, SUPERUSER_ID, vals, context=context)
        except Exception as e:
            raise WebServiceException(uid, 'Membership Request', 'ERROR-CREATE', e.message)
        return res

    @web_service
    def get_uid(self, cr, uid, email, birth_date, context=None):
        partner_obj = self.pool['res.partner']
        try:
            res = partner_obj.get_uid(cr, SUPERUSER_ID, email, birth_date, context=context)
        except Exception as e:
            raise WebServiceException(uid, "User's UID", 'ERROR CONNECT', e.message)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
