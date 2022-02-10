# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests.common import SavepointCase


class TestMassMailing(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cron_id = cls.env.ref(
            "mozaik_mass_mailing_bounce_counter.ir_cron_res_partner_email_bounced"
        )

        # deactivate other mass mailings to avoid messing with crons
        cls.env["mailing.mailing"].search([]).unlink()

    def setUp(self):
        super().setUp()
        self.thierry = self.browse_ref("mozaik_address.res_partner_thierry")
        self.paul = self.browse_ref("mozaik_address.res_partner_paul")
        self.marc = self.browse_ref("mozaik_address.res_partner_marc")
        self.mass_mailing = self.env["mailing.mailing"].create(
            {"subject": "Test mailing"}
        )

        # Thierry: mail was sent but counldn't reach the server -> then bounced
        self.mt1 = self.env["mailing.trace"].create(
            {
                "mass_mailing_id": self.mass_mailing.id,
                "model": "res.partner",
                "res_id": self.thierry.id,
                "sent": datetime.now() - relativedelta(days=1),
                "bounced": datetime.now() - relativedelta(hours=10),
            }
        )

        # Paul: mail was correctly sent
        self.mt2 = self.env["mailing.trace"].create(
            {
                "mass_mailing_id": self.mass_mailing.id,
                "model": "res.partner",
                "res_id": self.paul.id,
                "sent": datetime.now() - relativedelta(days=1),
            }
        )

        # Marc: mail was first bounced, but then sent successfully
        self.mt3 = self.env["mailing.trace"].create(
            {
                "mass_mailing_id": self.mass_mailing.id,
                "model": "res.partner",
                "res_id": self.marc.id,
                "sent": datetime.now() - relativedelta(hours=3),
                "bounced": datetime.now() - relativedelta(hours=10),
            }
        )

    def test_cron(self):
        """
        Due to setUp data, when the cron runs, it must
        - set counter to 0 for Marc and Paul, since they received the mail
        - increment counter for Thierry and set failure date
        """
        self.paul["email_bounced"] = 1
        self.thierry["email_bounced"] = 2
        self.marc["email_bounced"] = 3
        self.cron_id.lastcall = datetime.now() - relativedelta(days=2)
        self.cron_id.method_direct_trigger()

        self.assertEqual(self.paul.email_bounced, 0)
        self.assertEqual(self.thierry.email_bounced, 3)
        self.assertEqual(self.thierry.email_bounced_date, self.mt1.bounced)
        self.assertEqual(self.marc.email_bounced, 0)

        # When triggering the cron again, this mailing.traces were already treated
        # -> nothing changes
        self.paul["email_bounced"] = 2
        self.cron_id.method_direct_trigger()
        self.assertEqual(self.paul.email_bounced, 2)
        self.assertEqual(self.thierry.email_bounced, 3)
        self.assertEqual(self.marc.email_bounced, 0)
