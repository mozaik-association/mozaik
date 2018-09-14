# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from email.utils import formataddr
from odoo.tests.common import SavepointCase


class TestMassFunction(SavepointCase):

    def setUp(self):
        super(TestMassFunction, self).setUp()
        self.mfct_obj = self.env['distribution.list.mass.function']
        self.everybody_list = self.env.ref(
            'mozaik_communication.everybody_list')
        self.partner_obj = self.env['res.partner']

    def test_onchange_subject_and_template(self):
        vals = {
            'trg_model': 'email.coordinate',
            'e_mass_function': 'email_coordinate_id',
            'distribution_list_id': self.everybody_list.id,
        }
        wizard = self.mfct_obj.with_context(in_mozaik_user=True).create(vals)
        self.assertFalse(wizard.mass_mailing_name)
        subject = 'Le livre de la jungle'
        wizard.write({
            'subject': subject,
        })
        wizard._onchange_subject()
        self.assertEqual(subject, wizard.mass_mailing_name)
        wizard.write({
            'subject': 'La guerre des étoiles',
        })
        wizard._onchange_subject()
        # The mass_mailing_name should not change
        self.assertEqual(subject, wizard.mass_mailing_name)
        return

    def test_save_as_template(self):
        subject = str(uuid4())
        body = str(uuid4())
        vals = {
            'trg_model': 'email.coordinate',
            'e_mass_function': 'email_coordinate_id',
            'distribution_list_id': self.everybody_list.id,
            'subject': subject,
            'body': body,
        }
        wizard = self.mfct_obj.with_context(in_mozaik_user=True).create(vals)
        wizard.save_as_template()
        self.assertTrue(bool(wizard.email_template_id))
        self.assertEqual(wizard.email_template_id.subject, subject)
        # Use the 'IN' because the wizard can 'HTMLize' the result
        self.assertIn(body, wizard.email_template_id.body_html)
        return

    def test_email_from(self):
        """
        Check for:
        * partner_from_id content and default value
        * email_from computed value
        :return:
        """
        vals = {
            'name': 'Bob',
            'email': 'bob@vandersteen.be',
        }
        partner1 = self.partner_obj.create(vals)
        vals = {
            'name': 'Bobette',
            'email': 'bobette@vandersteen.be',
            'is_company': True,
        }
        partner2 = self.partner_obj.create(vals)
        # add a partner_id and a res_partner_ids to a distribution list
        everybody_list = self.everybody_list
        vals = {
            'partner_id': partner1.id,
            'res_partner_ids': [(6, 0, partner2.ids)],
        }
        everybody_list.write(vals)
        # from now, allowed "From" are:
        # - the parner of the list: bob
        # - authorized companies specified on the list: bobette
        # - the user because he is an owner of the list: admin

        # check for possible "From" choices
        mfct_obj = self.mfct_obj.with_context(
            active_model=everybody_list._name,
            active_id=everybody_list.id
        )
        partners = mfct_obj._get_partner_from()
        expected_partner = partner1 | partner2 | self.env.user.partner_id
        self.assertEqual(partners, expected_partner)
        # check for default value
        def_from = mfct_obj._get_default_partner_from_id()
        self.assertEqual(def_from, self.env.user.partner_id)
        # check for email_from
        partner_name = str(uuid4())
        vals = {
            'partner_from_id': partner2.id,
            'partner_name': partner_name,
        }
        wizard = mfct_obj.create(vals)
        wizard._onchange_partner_from()
        email = formataddr((partner_name, partner2.email))
        self.assertEqual(email, wizard.email_from)
        # check for possible "From" choices simulating a wizard reload
        mfct_obj = mfct_obj.with_context(
            active_model=mfct_obj._name,
            active_id=wizard.id,
        )
        partners = mfct_obj._get_partner_from()
        self.assertEqual(partners, expected_partner)
        vals = {
            'partner_id': False,
            'res_users_ids': [(5, 0, 0)],
        }
        everybody_list.write(vals)
        partner2.is_company = False
        # from now, allowed "From" are: nobody
        partners = mfct_obj._get_partner_from()
        # check for possible "From" choices
        self.assertFalse(partners)
        return
