# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.addons.mozaik_coordinate.tests.common_abstract_coordinate import \
    CommonAbstractCoordinate
from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestEmailCoordinate(CommonAbstractCoordinate, TransactionCase):

    def setUp(self):
        super(TestEmailCoordinate, self).setUp()
        self.model_coordinate = self.env['email.coordinate']
        self.coo_into_partner = 'email_coordinate_id'
        self.partner = self.env.ref("mozaik_coordinate.res_partner_thierry")
        self.field_id_1 = "%s@example.test" % str(uuid4())
        self.field_id_2 = "%s@example.test" % str(uuid4())
        self.field_id_3 = "%s@example.test" % str(uuid4())

    def test_bad_email(self):
        """
        Test to insert invalid email address (bad format) to check the
        constraint function _constrain_email()
        For this test, we try to insert invalid emails
        """
        with self.assertRaises(exceptions.ValidationError):
            self.model_coordinate.create({
                'partner_id': self.partner.id,
                'email': 'an invalid email',
            })
        with self.assertRaises(exceptions.ValidationError):
            self.model_coordinate.create({
                'partner_id': self.partner.id,
                'email': 'first bad AFTER right@ok.be',
            })
        return

    def test_valid_email(self):
        """
        Test to insert invalid email address (bad format) to check the
        constraint function _constrain_email()
        For this case we try to insert valid emails
        """
        self.model_coordinate.create({
            'partner_id': self.partner.id,
            'email': 'my123@example.test',
        })
        self.model_coordinate.create({
            'partner_id': self.partner.id,
            'email': 'another-titi@example.com',
        })
        return
