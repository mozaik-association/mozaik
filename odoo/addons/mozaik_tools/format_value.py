# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import string
import unicodedata
import re


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
