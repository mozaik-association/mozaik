# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class TestResPartner(TransactionCase):

    def test_compute_age(self):
        """
        Check for age depending on birthdate_date
        """
        age = 10
        ten_years_ago = date.today() - relativedelta(years=age)
        kim = self.env['res.partner'].create({
            'name': 'Jong-un Kim',
        })
        self.assertFalse(kim.age)

        def upd_age():
            kim.birthdate_date = datetime.strftime(
                ten_years_ago, DEFAULT_SERVER_DATE_FORMAT)

        upd_age()
        self.assertEqual(age, kim.age)
        ten_years_ago -= relativedelta(days=1)
        upd_age()
        self.assertEqual(age, kim.age)
        ten_years_ago += relativedelta(days=2)
        upd_age()
        self.assertEqual(age-1, kim.age)
        return

    def test_search_age(self):
        """
        Check for birthdate_date domain computed from an age domain
        """
        age = 10
        ten_years_ago = date.today() - relativedelta(years=age)
        birth_date = datetime.strftime(
            ten_years_ago, DEFAULT_SERVER_DATE_FORMAT)
        dom = self.env['res.partner']._search_age('<=', age)
        self.assertEqual(('birthdate_date', '>=', birth_date), dom[0])
        dom = self.env['res.partner']._search_age('>', age)
        self.assertEqual(('birthdate_date', '<', birth_date), dom[0])
        return
