# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestMailComposeMessage(SavepointCase):
    """
    Tests for mail.compose.message
    """

    def setUp(self):
        super().setUp()
        self.mail_composer_obj = self.env['mail.compose.message']
        self.partner_obj = self.env['res.partner']
        self.mail_obj = self.env['mail.mail']
        self.config_obj = self.env['ir.config_parameter']
        self.priorities_key = "mail.sending.job.priorities"
        self.priorities = priorities = {
            0: 500,
            10: 100,
            15: 80,
            20: 60,
            30: 50,
            40: 40,
        }
        self.config_obj.set_param(self.priorities_key, str(priorities))
        self.mail_obj.search([]).unlink()

    def _get_priority(self, active_ids):
        """
        Get the priority based on the priorities
        :param active_ids: list of int
        :return: int
        """
        priorities = self.priorities
        size = len(active_ids)
        limits = [lim for lim in priorities if lim <= size]
        return priorities.get(max(limits))

    def test_get_priorities1(self):
        """
        Test if the _get_priorities function correctly load priorities.
        For this case, we have a normal behaviour: valid dict into parameters
        :return:
        """
        priorities = self.mail_composer_obj._get_priorities()
        self.assertDictEqual(self.priorities, priorities)
        return

    def test_get_priorities2(self):
        """
        Test if the _get_priorities function correctly load priorities.
        For this case, it should raise an exception because the syntax is not
        correct.
        :return:
        """
        value = "{I don't have a valid format"
        self.config_obj.set_param(self.priorities_key, value)
        with self.assertRaises(exceptions.UserError):
            self.mail_composer_obj._get_priorities()
        return

    def test_get_priorities3(self):
        """
        Test if the _get_priorities function correctly load priorities.
        For this case, it should raise an exception because it's not a valid
        dict
        :return:
        """
        value = "I'm not a dict at all :)"
        self.config_obj.set_param(self.priorities_key, value)
        with self.assertRaises(exceptions.UserError):
            self.mail_composer_obj._get_priorities()
        return

    def test_mail_priority1(self):
        """
        Test if the mail.compose.message set correctly the priority on
        the new mail.mail.
        For this case, we simulate a normal behaviour (send email to some
        partners)
        :return:
        """
        context = self.env.context.copy()
        for limit in [1, 10]:
            partners = self.partner_obj.search([], limit=limit)
            context.update({
                'active_ids': partners.ids,
            })
            mail_composer_obj = self.mail_composer_obj.with_context(context)
            subject = "I'm not a SPAM-%s" % limit
            mail_composer_vals = {
                'email_from': 'my-unit-test@test.eu',
                'subject': subject,
                'model': 'res.partner',
                'composition_mode': 'mass_mail',
            }
            mail_composer = mail_composer_obj.create(mail_composer_vals)
            mail_composer.send_mail()
            new_mails = self.mail_obj.search([('subject', '=', subject)])
            # Ensure new mails are created
            self.assertTrue(new_mails)
            priority = [self._get_priority(partners.ids)]
            priorities = new_mails.mapped('mail_job_priority')
            self.assertEqual(set(priorities), set(priority))
        return

    def test_mail_priority2(self):
        """
        Test if the mail.compose.message set correctly the priority on
        the new mail.mail.
        For this case, we simulate a mail.compose.message without active_ids
        in the context
        :return:
        """
        context = self.env.context.copy()
        context.update({
            'active_ids': [],
        })
        mail_composer_obj = self.mail_composer_obj.with_context(context)
        mail_composer_vals = {
            'email_from': 'my-unit-test@test.eu',
            'subject': "I'm not a SPAM",
            'model': 'res.partner',
            'composition_mode': 'mass_mail',
        }
        mail_composer = mail_composer_obj.create(mail_composer_vals)
        # We should have the 'normal' exception about Singleton
        with self.assertRaises(ValueError) as e:
            mail_composer.send_mail()
        self.assertIn("singleton", str(e.exception))
        new_mails = self.mail_obj.search([])
        # Ensure no new mails are created
        self.assertFalse(new_mails)
        return
