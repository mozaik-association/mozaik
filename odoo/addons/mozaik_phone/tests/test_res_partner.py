# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo import fields


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.partner_model = self.env['res.partner']
        self.phone_model = self.env['phone.phone']
        self.phone_coordinate_model = self.env['phone.coordinate']
        self.partner_pauline = self.env.ref(
            "mozaik_coordinate.res_partner_pauline")
        self.partner_sandra = self.env.ref(
            "mozaik_coordinate.res_partner_sandra")
        self.phone2 = self.env.ref("mozaik_phone.phone_phone_fix5")
        self.coordinate1 = self.env.ref("mozaik_phone.phone_coordinate1")

    def test_create_phone_coordinate(self):
        """
        Test the fact that when a phone_coordinate is create for a partner,
        The phone value is right set
        """
        self.assertEquals(
            self.partner_pauline.phone, self.coordinate1.phone_id.name,
            "Phone Should Be Set With The Same Value")
        return

    def test_update_phone_coordinate(self):
        """
        Test the fact that when a phone_id is updated for a phone_coordinate
        The phone value is right set for the partner of this phone_coordinate
        """
        self.coordinate1.write({
            'phone_id': self.phone2.id,
        })
        self.assertEquals(
            self.partner_pauline.phone, self.coordinate1.phone_id.name,
            "Phone Should Be Set With The Same Value")
        return

    def test_update_phone_number(self):
        """
        Test the replication of the phone number of the main coordinate on
        the partner
        """
        self.coordinate1.write({
            'phone_id': self.phone2.id,
        })
        self.phone2.write({
            'name': '091452325',
        })
        self.assertEquals(
            self.partner_pauline.phone, self.coordinate1.phone_id.name,
            "Phone Should Be Set With The Same Value")
        self.phone2.write({
            'also_for_fax': True,
        })
        self.assertEquals(
            self.partner_pauline.fax,
            self.coordinate1.phone_id.name, "Phone and Fax must be identical")
        return
