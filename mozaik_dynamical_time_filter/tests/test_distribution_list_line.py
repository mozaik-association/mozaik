# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests.common import TransactionCase


class TestDistributionListLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env.ref("base.model_res_partner")
        self.dist_list_one = self.browse_ref("distribution_list.distribution_list_one")
        self.dist_list_two = self.browse_ref("distribution_list.distribution_list_two")
        domain = [
            ("name", "=", "self"),
            ("relation", "=", "res.partner"),
            ("model_id", "=", "res.partner"),
        ]
        bridge_field_id = self.env["ir.model.fields"].search(domain)
        src_model_id = self.env["ir.model"].search([("model", "=", "res.partner")])
        # This filter looks for partners whose field date is equal to today.
        self.dist_list_line_today = self.env["distribution.list.line"].create(
            {
                "name": "Date equal to Today",
                "distribution_list_id": self.dist_list_one.id,
                "domain_widget": "['&',['date','>=','2021-11-09 00:00:00'],"
                "['date','<=','2021-11-09 23:59:59']]",
                "manually_edit_domain": False,
                "bridge_field_id": bridge_field_id.id,
                "src_model_id": src_model_id.id,
            }
        )
        self.dist_list_line_today.write(
            {
                "manually_edit_domain": True,
                "domain_handwritten": "['&',['date','>=',"
                "context_today().strftime('%Y-%m-%d 00:00:00')],"
                "['date','<=',context_today().strftime('%Y-%m-%d 23:59:59')]]",
            }
        )

        # This filter looks for partners whose field date is less than 30 days ago.
        self.dist_list_line_30_days = self.env["distribution.list.line"].create(
            {
                "name": "Date Less than 30 Days",
                "distribution_list_id": self.dist_list_two.id,
                "domain_widget": "[['date','>=','2021-10-09 00:00:00']]",
                "bridge_field_id": bridge_field_id.id,
                "src_model_id": src_model_id.id,
            }
        )
        self.dist_list_line_30_days.write(
            {
                "domain_handwritten": "[['date','>=',"
                "(context_today() - relativedelta(days=30)).strftime('%Y-%m-%d 00:00:00')]]",
                "manually_edit_domain": True,
            }
        )
        # Creation of two contacts with different date values

        self.first_date = date(2021, 4, 12)
        self.partnerDoe = (self.env["res.partner"]).create(
            {
                "lastname": "Doe",
                "firstname": "Dave",
                "email": "dave.doe@example.com",
                "date": self.first_date,
            }
        )
        self.second_date = date(2021, 5, 15)
        self.partnerSmith = (self.env["res.partner"]).create(
            {
                "lastname": "Smith",
                "firstname": "John",
                "email": "john.smith@example.com",
                "date": self.second_date,
            }
        )

    def test_filter_today(self):
        """
        Data:
            self.partnerJoe: a partner whose date field is one month earlier
            self.partnerSmith: a partner whose date field is equal to today
            self.dist_list_line_today, a filter for contacts whose date
                equals today.
        Test case:
            When filtering with self.dis_list_line_today, we want to obtain
            a unique record: self.partnerSmith.
        """
        with freeze_time(self.second_date):
            targ_rec = self.dist_list_line_today._get_target_recordset()
            self.assertEqual(len(targ_rec), 1, "One partner should verify the filter.")
            self.assertEqual(
                targ_rec[0].lastname, "Smith", "The target record should be Smith."
            )

    def test_filter_less_than_30_days(self):
        """
        Data:
            self.partnerJoe: a partner whose date field is more than one month earlier
            self.partnerSmith: a partner whose date field is equal to today
            self.dist_list_line_30_days, a filter for contacts whose date
               is less than 30 days from today.
        Test case:
            When filtering with self.dis_list_line_30_days, we want to obtain
            a unique record: self.partnerSmith.
        """
        with freeze_time(self.second_date):
            targ_rec = self.dist_list_line_30_days._get_target_recordset()
            self.assertEqual(len(targ_rec), 1, "One partner should verify the filter.")
            self.assertEqual(
                targ_rec[0].lastname, "Smith", "The target record should be Smith."
            )

    def test_filter_less_than_30_days_after_some_days(self):
        """
        Data:
            self.partnerJoe: a partner whose date field is more than one month earlier
            self.partnerSmith: a partner whose date field is 4 days earlier
            self.dist_list_line_30_days, a filter for contacts whose date
                has less than 30 days from today.
        Test case:
            When filtering with self.dis_list_line_30_days, we want to obtain
            a unique record: self.partnerSmith.
        """
        actual_date = self.second_date + relativedelta(days=4)
        with freeze_time(actual_date):
            targ_rec = self.dist_list_line_30_days._get_target_recordset()
            self.assertEqual(len(targ_rec), 1, "One partner should verify the filter.")
            self.assertEqual(
                targ_rec[0].lastname, "Smith", "The target record should be Smith."
            )

    def test_filter_less_than_30_days_later(self):
        """
        Data:
            self.partnerJoe: a partner whose date field is more than three months earlier
            self.partnerSmith: a partner whose date field is 2 months earlier
            self.dist_list_line_30_days, a filter for contacts whose date
                is less than 30 days from today.
            Test case:
                When filtering with self.dis_list_line_30_days, we want to obtain
                no record.
        """
        actual_date = self.second_date + relativedelta(months=2)
        with freeze_time(actual_date):
            targ_rec = self.dist_list_line_30_days._get_target_recordset()
            self.assertEqual(len(targ_rec), 0, "No partner should verify the filter.")
