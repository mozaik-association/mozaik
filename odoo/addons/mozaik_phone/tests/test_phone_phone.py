# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestPhonePhone(TransactionCase):

    def setUp(self):
        super(TestPhonePhone, self).setUp()
        self.model_phone = self.env['phone.phone']

    def test_insert_without_prefix(self):
        """
        Test case:
        insert a valid phone number without prefix
        """
        num = self.model_phone._check_and_format_number('061140220')
        self.assertEquals(num, '+32 61 14 02 20',
                          '061140220 should give +32 61 14 02 20')
        return

    def test_insert_with_prefix(self):
        """
        Test case:
        insert a valid phone number with prefix
        insert: +32489587520
        expected: +32 489 58 75 20
        """
        num = self.model_phone._check_and_format_number('+32489587520')
        self.assertEquals(num, '+32 489 58 75 20',
                          '+32489587520 should give +32 489 58 75 20')
        return

    def test_proper_escaping(self):
        """
        Test case:
        insert a valid phone number with other characters in more
        insert: 061-54/10    45
        expected: +32 61 54 10 45
        """
        num = self.model_phone._check_and_format_number(
            '061-54/10    45')
        self.assertEquals(num, '+32 61 54 10 45',
                          '061-54/10    45 should give +32 61 54 10 45')
        return

    def test_insert_bad_query(self):
        """
        Test case:
        insert a bad format for a phone e.g. a word
        insert: badquery (str)
        expected: orm_exception
        """
        with self.assertRaises(exceptions.UserError):
            self.model_phone._check_and_format_number('badquery')
        return
