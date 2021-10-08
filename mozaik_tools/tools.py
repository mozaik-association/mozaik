# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import re
import string
import unicodedata
from datetime import date

from odoo import _
from odoo.exceptions import UserError
from odoo.tools.mail import single_email_re

_logger = logging.getLogger(__name__)
try:
    import phonenumbers as pn
except (ImportError, IOError) as err:
    _logger.debug(err)


CHARS_TO_ESCAPE = re.compile(r"[%s\s]+" % re.escape(string.punctuation))
CHARS_AND_DIGIT_TO_ESCAPE = re.compile(r"[%s\s\d]+" % re.escape(string.punctuation))


def format_value(value, escape_digit=False, remove_blanks=False):
    """
    Upper to lower case for value stripping all special characters to one space
    :type value: char
    :rtype: char
    """
    if value:
        value = "".join(
            c
            for c in unicodedata.normalize("NFD", str(value))
            if unicodedata.category(c) != "Mn"
        )
        esc = "" if remove_blanks else " "
        regexp = CHARS_AND_DIGIT_TO_ESCAPE if escape_digit else CHARS_TO_ESCAPE
        value = re.sub(regexp, esc, value)
        value = value.strip().lower()
    return value


def check_and_format_number(num, default_country_code):
    """
    Number formatted into a International Number
    If number is not starting by '+' then check if it starts by
    '00'
    and replace it with '+'. Otherwise set a code value with
    a PREFIX
    :param num: str
    :return: str
    """
    code = False
    numero = num
    if num[:2] == "00":
        numero = "%s%s" % (num[:2].replace("00", "+"), num[2:])
    elif not num.startswith("+"):
        code = default_country_code
    try:
        normalized_number = pn.parse(numero, code) if code else pn.parse(numero)
    except pn.NumberParseException as e:
        errmsg = _("Invalid phone number: %s") % e
        raise UserError(errmsg)
    return pn.format_number(normalized_number, pn.PhoneNumberFormat.INTERNATIONAL)


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
    value = value.replace(" ", "")
    return value


def check_email(email):
    return re.match(single_email_re, email) is not None


def get_age(birth_date):
    """
    compute age depending of the birth_date and today
    """
    if not birth_date:
        return False
    today = date.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
