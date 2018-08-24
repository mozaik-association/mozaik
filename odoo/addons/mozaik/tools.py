# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import string
import unicodedata
import re


CHARS_TO_ESCAPE = re.compile(r'[%s\s]+' % re.escape(string.punctuation))
CHARS_AND_DIGIT_TO_ESCAPE = re.compile(
    r'[%s\s\d]+' % re.escape(string.punctuation))


def format_value(value, escape_digit=False, remove_blanks=False):
    """
    Upper to lower case for value stripping all special characters to one space
    :type value: char
    :rtype: char
    """
    if value:
        value = ''.join(
            c
            for c in unicodedata.normalize('NFD', value)
            if unicodedata.category(c) != 'Mn'
        )
        esc = not remove_blanks and ' ' or ''
        regexp = escape_digit and CHARS_AND_DIGIT_TO_ESCAPE or CHARS_TO_ESCAPE
        value = re.sub(regexp, esc, value)
        value = value.strip().lower()
    return value
