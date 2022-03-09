# Part of Odoo. See LICENSE file for full copyright and licensing details.


from datetime import date

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests import common

from odoo.addons.mail.tests.common import MockEmail, mail_new_test_user


class TestPetitionCommon(common.SavepointCase, MockEmail):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_petitionmanager = mail_new_test_user(
            cls.env,
            login="user_petitionmanager",
            name="Martine PetitionManager",
            email="martine.petitionmanager@test.example.com",
            notification_type="inbox",
            company_id=cls.env.ref("base.main_company").id,
            groups="base.group_user,mozaik_petition.group_petition_manager",
        )

        cls.petition_cron_id = cls.env.ref("mozaik_petition.petition_mail_scheduler")

        # deactivate other schedulers to avoid messing with crons
        cls.env["petition.mail"].search([]).unlink()

    def setUp(self):
        super().setUp()
        # freeze some datetimes, and ensure more than 1 day before petition starts
        # to ease time-based scheduler check
        self.today = date(2021, 9, 18)
        self.petition_date_begin = date(2021, 9, 22)
        self.petition_date_end = date(2021, 9, 24)
        self.milestone = self.env["petition.milestone"].create({"value": 1})

        # create a petition
        with freeze_time(self.today):
            self.test_petition = (
                self.env["petition.petition"]
                .with_user(self.user_petitionmanager)
                .create(
                    {
                        "title": "TestPetitionMail",
                        "date_begin": self.petition_date_begin,
                        "date_end": self.petition_date_end,
                        "milestone_ids": [(6, 0, self.milestone.id)],
                        "petition_mail_ids": [
                            (
                                0,
                                0,
                                {  # right at subscription
                                    "interval_unit": "now",
                                    "interval_type": "after_sub",
                                    "template_id": self.env[
                                        "ir.model.data"
                                    ].xmlid_to_res_id(
                                        "mozaik_petition.petition_subscription"
                                    ),
                                },
                            ),
                            (
                                0,
                                0,
                                {  # one day after subscription
                                    "interval_nbr": 1,
                                    "interval_unit": "days",
                                    "interval_type": "after_sub",
                                    "template_id": self.env[
                                        "ir.model.data"
                                    ].xmlid_to_res_id(
                                        "mozaik_petition.petition_subscription"
                                    ),
                                },
                            ),
                            (
                                0,
                                0,
                                {  # one day before petition
                                    "interval_nbr": 1,
                                    "interval_unit": "days",
                                    "interval_type": "before_petition",
                                    "template_id": self.env[
                                        "ir.model.data"
                                    ].xmlid_to_res_id(
                                        "mozaik_petition.petition_subscription"
                                    ),
                                },
                            ),
                            (
                                0,
                                0,
                                {  # one day after petition
                                    "interval_nbr": 1,
                                    "interval_unit": "days",
                                    "interval_type": "after_petition",
                                    "template_id": self.env[
                                        "ir.model.data"
                                    ].xmlid_to_res_id(
                                        "mozaik_petition.petition_subscription"
                                    ),
                                },
                            ),
                        ],
                    }
                )
            )

        # subscription schedulers
        self.after_sub_scheduler = self.env["petition.mail"].search(
            [
                ("petition_id", "=", self.test_petition.id),
                ("interval_type", "=", "after_sub"),
                ("interval_unit", "=", "now"),
            ]
        )
        self.after_sub_scheduler_2 = self.env["petition.mail"].search(
            [
                ("petition_id", "=", self.test_petition.id),
                ("interval_type", "=", "after_sub"),
                ("interval_unit", "=", "days"),
            ]
        )

        # before petition scheduler
        self.petition_prev_scheduler = self.env["petition.mail"].search(
            [
                ("petition_id", "=", self.test_petition.id),
                ("interval_type", "=", "before_petition"),
            ]
        )

        # after petition scheduler
        self.petition_next_scheduler = self.env["petition.mail"].search(
            [
                ("petition_id", "=", self.test_petition.id),
                ("interval_type", "=", "after_petition"),
            ]
        )

    def _create_registrations(self):
        # create two registrations at time of petition creation
        with freeze_time(self.today), self.mock_mail_gateway():
            self.reg1 = (
                self.env["petition.registration"]
                .with_user(self.user_petitionmanager)
                .create(
                    {
                        "petition_id": self.test_petition.id,
                        "lastname": "Reg1",
                        "firstname": "r1",
                        "email": "reg1@example.com",
                    }
                )
            )
            self.reg2 = (
                self.env["petition.registration"]
                .with_user(self.user_petitionmanager)
                .create(
                    {
                        "petition_id": self.test_petition.id,
                        "lastname": "Reg2",
                        "firstname": "r2",
                        "email": "reg2@example.com",
                    }
                )
            )

    def _create_third_registration(self):
        # create a registration one day before the petition starts
        today_start = self.petition_date_begin + relativedelta(days=-1)
        with freeze_time(today_start), self.mock_mail_gateway():
            self.reg3 = (
                self.env["petition.registration"]
                .with_user(self.user_petitionmanager)
                .create(
                    {
                        "petition_id": self.test_petition.id,
                        "lastname": "Reg3",
                        "firstname": "r3",
                        "email": "reg3@example.com",
                    }
                )
            )
