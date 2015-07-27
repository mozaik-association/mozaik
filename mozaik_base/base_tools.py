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
import string
import unicodedata
import re

from datetime import datetime, date
from openerp.tools.mail import single_email_re
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT


CHARS_TO_ESCAPE = re.compile(r'[%s\s]+' % re.escape(string.punctuation))
CHARS_AND_DIGIT_TO_ESCAPE = re.compile(
    r'[%s\s\d]+' % re.escape(string.punctuation))


def format_value(value, escape_digit=False, remove_blanks=False):
    """
    :type value: char
    :rtype: char
    :rparam: upper to lower case for value stripping all special characters
             to one space
    """
    if value:
        value = ''.join(c for c in unicodedata.normalize('NFD', u'%s' % value)
                        if unicodedata.category(c) != 'Mn')
        esc = not remove_blanks and ' ' or ''
        regexp = escape_digit and CHARS_AND_DIGIT_TO_ESCAPE or CHARS_TO_ESCAPE
        value = re.sub(regexp, esc, value)
        value = value.lower().strip()
    return value


def format_email(value):
    """
    ============
    format_email
    ============
    :type value: char
    :rtype: char
    :rparam value: value without space and in lower case
    """
    value = value.lower().strip()
    value = value.replace(' ', '')
    return value


def check_email(email):
    return re.match(single_email_re, email) is not None


def get_age(birth_date):
    """
    compute age depending of the birth_date and today
    """
    born = datetime.strptime(birth_date, DEFAULT_SERVER_DATE_FORMAT)
    today = date.today()
    return today.year - born.year -\
        ((today.month, today.day) < (born.month, born.day))
